import pymysql
from dbutils.pooled_db import PooledDB

from model import DatabaseConfig
from strategy import DatabaseStrategy


class MySQLStrategy(DatabaseStrategy):

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.pool = None

    def create_pool(self) -> PooledDB:
        if not self.pool:
            self.pool = PooledDB(
                creator=pymysql,
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                mincached=self.config.minCached or 5,
                maxcached=self.config.maxCached or 10,
                maxconnections=self.config.maxConnections or 20,
            )
        return self.pool

    def get_connection(self) -> pymysql.connections.Connection:
        if not self.pool:
            self.create_pool()
        return self.pool.connection()

    def close_connection(self, connection: object) -> None:
        if connection:
            connection.close()

    def list_tables(self) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT TABLE_NAME, TABLE_COMMENT
                    FROM information_schema.tables
                    WHERE TABLE_SCHEMA = %s
                    """,
                    (self.config.database,),
                )
            tables = cursor.fetchall()

            headers = ["TABLE_NAME", "TABLE_COMMENT"]
            return self.format_table(headers, list(tables))
        finally:
            self.close_connection(connection)

    def describe_Table(self, table_name: str) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COLUMN_NAME,
                           COLUMN_COMMENT,
                           DATA_TYPE,
                           COLUMN_TYPE,
                           COLUMN_DEFAULT,
                           COLUMN_KEY,
                           IS_NULLABLE,
                           EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                      AND TABLE_NAME = %s;
                    """,
                    (
                        self.config.database,
                        table_name,
                    ),
                )
                table_infos = cursor.fetchall()

                result_infos = []

                for table_info in table_infos:
                    cursor.execute(
                        """
                        SELECT INDEX_NAME
                        FROM INFORMATION_SCHEMA.STATISTICS
                        WHERE TABLE_SCHEMA = %s
                          AND TABLE_NAME = %s
                          AND COLUMN_NAME = %s
                        """,
                        (
                            self.config.database,
                            table_name,
                            table_info[0],
                        ),
                    )
                    index_results = cursor.fetchall()

                    index_names = [row[0] for row in index_results]

                    if index_names:
                        info_list = list(table_info)
                        if info_list[5]:
                            info_list[5] = f"{info_list[5]} ({', '.join(index_names)})"
                        result_infos.append(tuple(info_list))
                    else:
                        result_infos.append(table_info)

                headers = [
                    "COLUMN_NAME",
                    "COLUMN_COMMENT",
                    "DATA_TYPE",
                    "COLUMN_TYPE",
                    "COLUMN_DEFAULT",
                    "COLUMN_KEY",
                    "IS_NULLABLE",
                    "EXTRA",
                ]
            return self.format_table(headers, result_infos)
        finally:
            self.close_connection(connection)

    def execute_sql(self, sql: str, params: tuple = None) -> str:
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                sql_stripped = sql.strip()
                if sql_stripped.upper().startswith("SELECT"):
                    cursor.execute(sql_stripped, params)
                    column_names = [desc[0] for desc in cursor.description]
                    result = cursor.fetchall()
                    return self.format_table(column_names, list(result))
                else:
                    connection.begin()
                    affected_rows = cursor.execute(sql_stripped, params)
                    return self.format_update(affected_rows)
        finally:
            self.close_connection(connection)
