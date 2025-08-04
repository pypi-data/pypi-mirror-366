import os
import sys
from dotenv import load_dotenv
from src.factory import DatabaseStrategyFactory
from mcp.server.fastmcp import FastMCP

load_dotenv()


def parse_args():
    """解析命令行参数，支持 key=value 格式"""
    config = {}
    for arg in sys.argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            config[key] = value
    return config


def get_db_config():
    """从命令行参数、环境变量获取数据库配置，提供默认值"""
    # 1. 默认值
    config = {

    }

    # 2. 环境变量覆盖默认值
    for key in config.keys():
        env_value = os.getenv(key)
        if env_value:
            config[key] = env_value

    # 3. 命令行参数优先级最高
    args_config = parse_args()
    config.update(args_config)

    # 4. 转换端口为整数
    config['port'] = int(config['port'])

    return config


# 获取配置
config = get_db_config()

# 初始化数据库策略
strategy = DatabaseStrategyFactory.get_database_strategy(
    config['db_type'],
    host=config['host'],
    port=config['port'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)

mcp = FastMCP("database-mcp")


@mcp.tool(description="List all tables in the database")
def list_tables() -> str:
    """Retrieve a list of all tables in the connected database"""
    return strategy.list_tables()


@mcp.tool(description="Describe the structure of a specific table")
def describe_Table(table_name: str) -> str:
    """Show the schema and column information for a given table"""
    return strategy.describe_Table(table_name)


@mcp.tool(description="Execute a SQL statement and return results")
def execute_sql(sql: str, params: tuple = None) -> str:
    """Execute custom SQL queries with optional parameters and return formatted results"""
    return strategy.execute_sql(sql, params)


def main():
    """MCP 服务主入口"""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
