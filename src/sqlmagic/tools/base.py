from abc import ABC, abstractmethod
from typing import List

from mcp.types import TextContent

from ..core.config import Config
from ..core.connection import ConnectionManager


class BaseTool(ABC):
    def __init__(self, connection_manager: ConnectionManager, config: Config):
        self.connection_manager = connection_manager
        self.config = config

    @abstractmethod
    async def execute(self, **kwargs) -> List[TextContent]:
        pass

    def validate_connection(self, connection_name: str):
        if not self.connection_manager.is_connected(connection_name):
            raise ValueError(f"Connection {connection_name} not found or inactive")
