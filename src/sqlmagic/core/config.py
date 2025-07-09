import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    log_level: str = "INFO"
    max_connections: int = 10
    query_timeout: int = 30
    max_rows_limit: int = 10000
    chart_width: int = 10
    chart_height: int = 6
    
    @classmethod
    def from_env(cls):
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_connections=int(os.getenv("MAX_CONNECTIONS", "10")),
            query_timeout=int(os.getenv("QUERY_TIMEOUT", "30")),
            max_rows_limit=int(os.getenv("MAX_ROWS_LIMIT", "10000")),
            chart_width=int(os.getenv("CHART_WIDTH", "10")),
            chart_height=int(os.getenv("CHART_HEIGHT", "6"))
        )