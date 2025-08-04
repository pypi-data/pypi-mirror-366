from typing import Any, List, Tuple
from abc import ABC, abstractmethod
from dbutils.pooled_db import PooledDB

from src.model import DatabaseConfig


class DatabaseStrategy(ABC):
    """数据库连接策略抽象基类"""

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @abstractmethod
    def create_pool(self) -> PooledDB:
        """创建并返回数据库连接池"""
        pass

    @abstractmethod
    def get_connection(self) -> Any:
        """从连接池获取一个数据库连接"""
        pass

    @abstractmethod
    def list_tables(self) -> str:
        """查询数据库字段"""
        pass

    @abstractmethod
    def describe_Table(self, table_name: str) -> str:
        """查询表字段信息"""
        pass

    @abstractmethod
    def close_connection(self, connection: object) -> None:
        """关闭连接"""
        pass

    @abstractmethod
    def execute_sql(self, sql: str, params: tuple = None) -> str:
        pass

    @staticmethod
    def format_table(headers: List[str], rows: List[Tuple]) -> str:
        result = []

        if not rows:
            return ""

        def get_display_width(text: str) -> int:
            """计算字符串的显示宽度，中文字符算2个宽度"""
            width = 0
            for char in text:
                if ord(char) > 127:
                    width += 2
                else:
                    width += 1
            return width

        def pad_string(text: str, target_width: int) -> str:
            """按显示宽度填充字符串"""
            current_width = get_display_width(text)
            padding_needed = target_width - current_width
            return text + " " * padding_needed

        col_widths = []
        for i, header in enumerate(headers):
            max_width = get_display_width(header)
            for row in rows:
                cell_value = str(row[i]) if row[i] is not None else ""
                max_width = max(max_width, get_display_width(cell_value))
            col_widths.append(max_width)

        header_parts = []
        for i in range(len(headers)):
            padded_header = pad_string(headers[i], col_widths[i])
            header_parts.append(padded_header)
        header_line = " | ".join(header_parts)
        result.append(header_line)

        separator = " | ".join("-" * col_widths[i] for i in range(len(headers)))
        result.append(separator)

        for row in rows:
            row_parts = []
            for i in range(len(headers)):
                cell_value = str(row[i]) if row[i] is not None else ""
                padded_cell = pad_string(cell_value, col_widths[i])
                row_parts.append(padded_cell)
            row_line = " | ".join(row_parts)
            result.append(row_line)

        return "\n".join(result)

    @staticmethod
    def format_update(affected_rows: int) -> str:
        return f"成功修改了 {affected_rows} 条数据记录"
