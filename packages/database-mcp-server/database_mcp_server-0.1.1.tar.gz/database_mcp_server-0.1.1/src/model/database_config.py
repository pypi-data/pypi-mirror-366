from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """数据库配置类"""

    host: str
    port: int
    user: str
    password: str
    database: str
    minCached: Optional[int] = None
    maxCached: Optional[int] = None
    maxConnections: Optional[int] = None
