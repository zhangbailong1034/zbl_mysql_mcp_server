# <font style="color:rgb(31, 35, 40);">zbl_mysql_mcp_server</font>
<font style="color:rgb(31, 35, 40);">本地 MySQL MCP 服务器（基于 python开发，使用stdio协议） 提供数据库查询、执行、表结构查看等工具。 使用环境变量配置数据库连接。</font>

# 本地环境
+ windows 11
+ mysql server 8.0.3
+ python >=3.12.4
+ uv >= 0.8.12



# 使用指南

## 确认环境
```
python -V //python 3.12.4
uv -V   //uv 0.8.12
mysql -V //mysql  Ver 8.0.41 for Win64 on x86_64 (MySQL Community Server - GPL)
```

## 下载源码
```bash
git clone https://github.com/zhangbailong1034/zbl_mysql_mcp_server.git
uv sync
```

## Qoder使用
```
mcp.json
{
  "mcpServers": {
      "mysql": {
      "command": "D:/mcpProjects/zbl_mysql_mcp_server/.venv/Scripts/python.exe",
      "args": ["D:/mcpProjects/zbl_mysql_mcp_server/main.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_db_name"
      }
    }
  }
}
```

## DeepSeek-Tui使用
mcp.json

```json

{
  "timeouts": {
    "connect_timeout": 10,
    "execute_timeout": 60,
    "read_timeout": 120
  },
  "servers": {
    "mysql": {
      "command": "D:/mcpProjects/zbl_mysql_mcp_server/.venv/Scripts/python.exe",
      "args": ["D:/mcpProjects/zbl_mysql_mcp_server/main.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_db_name"
      }
    }
  }
}
```



## Trae使用
mcp.json

``` json
{
  "mcpServers": {
      "mysql": {
      "command": "D:/mcpProjects/zbl_mysql_mcp_server/.venv/Scripts/python.exe",
      "args": ["D:/mcpProjects/zbl_mysql_mcp_server/main.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_db_name"
      }
    }
  }
}
```
