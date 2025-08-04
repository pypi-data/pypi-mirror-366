import os
from dotenv import load_dotenv
from src.factory import DatabaseStrategyFactory
from mcp.server.fastmcp import FastMCP

load_dotenv()


def get_db_config():
    return {
        'db_type': os.getenv('db_type'),
        'host': os.getenv('host'),
        'port': int(os.getenv('port')),
        'user': os.getenv('user'),
        'password': os.getenv('password'),
        'database': os.getenv('database')
    }


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
