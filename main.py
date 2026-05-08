#!/usr/bin/env python3
"""
本地 MySQL MCP 服务器（基于 stdio）
提供数据库查询、执行、表结构查看等工具。
使用环境变量配置数据库连接。
"""

import os
import json
import mysql.connector
from mysql.connector import Error
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# ---------- 数据库连接配置（从环境变量读取）----------
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "test"),
    "charset": "utf8mb4",
    "use_unicode": True,
}

# 全局只读模式（可选，建议生产环境开启）
READ_ONLY = os.getenv("MYSQL_READ_ONLY", "false").lower() == "true"

# ---------- 数据库辅助函数 ----------
def get_db_connection():
    """创建并返回 MySQL 数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"数据库连接失败: {e}")

def execute_select(sql: str, params: tuple = None):
    """执行 SELECT 查询，返回结果列表（每行为字典）"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()

def execute_write(sql: str, params: tuple = None):
    """执行 INSERT/UPDATE/DELETE，返回影响行数"""
    if READ_ONLY:
        raise Exception("服务器处于只读模式，不允许执行写操作")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise Exception(f"SQL执行失败: {e}")
    finally:
        cursor.close()
        conn.close()

def list_tables():
    """获取当前数据库中所有表名"""
    result = execute_select(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = %s",
        (DB_CONFIG["database"],)
    )
    return [row["table_name"] for row in result]

def describe_table(table_name: str):
    """获取表结构信息（字段名、类型、是否为空、键、默认值、额外）"""
    result = execute_select(f"DESCRIBE {mysql.connector.conversion.MySQLConverter.escape(table_name)}")
    return result  # 已经是字典列表

# ---------- MCP 服务器定义 ----------
# 创建服务器实例
server = Server("mysql-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出所有可用工具
    MCP 客户端通过此接口发现服务器提供的功能
    """
    return [
        types.Tool(
            name="query",
            description="执行只读的 SELECT 查询，返回 JSON 格式的结果集。适用于数据查询、统计分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "完整的 SELECT SQL 语句"},
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="execute",
            description="执行写操作（INSERT, UPDATE, DELETE），返回受影响的行数。注意：只在非只读模式下可用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "INSERT/UPDATE/DELETE SQL 语句"},
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="list_tables",
            description="列出当前数据库中的所有表名。",
            inputSchema={
                "type": "object",
                "properties": {},  # 无参数
            },
        ),
        types.Tool(
            name="describe_table",
            description="查看指定表的结构（字段名、类型、键等信息）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "表名"},
                },
                "required": ["table_name"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """
    处理具体的工具调用请求
    """
    if not arguments:
        arguments = {}

    try:
        if name == "query":
            sql = arguments.get("sql")
            if not sql:
                raise ValueError("缺少 sql 参数")
            # 简单安全检查：只允许 SELECT
            if not sql.strip().upper().startswith("SELECT"):
                raise ValueError("query 工具只能执行 SELECT 语句")
            rows = execute_select(sql)
            result = json.dumps(rows, ensure_ascii=False, default=str)
            return [types.TextContent(type="text", text=result)]

        elif name == "execute":
            sql = arguments.get("sql")
            if not sql:
                raise ValueError("缺少 sql 参数")
            # 禁止 SELECT
            if sql.strip().upper().startswith("SELECT"):
                raise ValueError("execute 工具不能执行 SELECT，请使用 query 工具")
            affected = execute_write(sql)
            return [types.TextContent(type="text", text=f"✅ 执行成功，影响行数: {affected}")]

        elif name == "list_tables":
            tables = list_tables()
            result = json.dumps(tables, ensure_ascii=False)
            return [types.TextContent(type="text", text=result)]

        elif name == "describe_table":
            table_name = arguments.get("table_name")
            if not table_name:
                raise ValueError("缺少 table_name 参数")
            schema = describe_table(table_name)
            result = json.dumps(schema, ensure_ascii=False, default=str)
            return [types.TextContent(type="text", text=result)]

        else:
            raise ValueError(f"未知的工具: {name}")

    except Exception as e:
        # 返回错误信息给客户端
        return [types.TextContent(type="text", text=f"❌ 错误: {str(e)}")]

# ---------- 主入口 ----------
async def main():
    """
    启动 stdio 服务
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mysql-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())