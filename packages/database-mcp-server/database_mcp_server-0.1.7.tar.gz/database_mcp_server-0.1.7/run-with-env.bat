@echo off
echo 设置环境变量并启动 Database MCP Server...

set db_type=mysql
set host=192.168.31.50
set port=3306
set user=root
set password=Aa040832@
set database=mall_admin

echo 配置信息:
echo - 数据库类型: %db_type%
echo - 主机: %host%
echo - 端口: %port%
echo - 用户: %user%
echo - 数据库: %database%
echo.

database-mcp-server