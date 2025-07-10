import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import Tool
from mcp.types import TextContent

from .core.config import Config
from .core.connection import ConnectionManager
from .tools.basic import (
    AnalyzeDataTool,
    ConnectTool,
    DescribeTableTool,
    ExecuteQueryTool,
    ExploreTablesTool,
    SampleDataTool,
)
from .tools.analytics import (
    DetectAnomaliesTool,
    FindCorrelationsTool,
    TimeSeriesAnalysisTool,
)

logger = logging.getLogger(__name__)


class PostgreSQLMCPServer:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.connection_manager = ConnectionManager()
        self.tools = self._init_tools()
        self.server = Server("postgresql-analytics")
        self._setup_handlers()

    def _init_tools(self):
        return {
            "connect_database": ConnectTool(self.connection_manager, self.config),
            "explore_tables": ExploreTablesTool(self.connection_manager, self.config),
            "describe_table": DescribeTableTool(self.connection_manager, self.config),
            "sample_data": SampleDataTool(self.connection_manager, self.config),
            "analyze_data": AnalyzeDataTool(self.connection_manager, self.config),
            "execute_query": ExecuteQueryTool(self.connection_manager, self.config),
            "find_correlations": FindCorrelationsTool(self.connection_manager, self.config),
            "detect_anomalies": DetectAnomaliesTool(self.connection_manager, self.config),
            "time_series_analysis": TimeSeriesAnalysisTool(self.connection_manager, self.config),
        }

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="connect_database",
                    description="Connect to PostgreSQL database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "host": {"type": "string"},
                            "port": {"type": "integer", "default": 5432},
                            "database": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": [
                            "connection_name",
                            "host",
                            "database",
                            "username",
                            "password",
                        ],
                    },
                ),
                Tool(
                    name="explore_tables",
                    description="List all tables in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {"connection_name": {"type": "string"}},
                        "required": ["connection_name"],
                    },
                ),
                Tool(
                    name="describe_table",
                    description="Get table structure and column information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="sample_data",
                    description="Get sample data from a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                            "limit": {"type": "integer", "default": 10},
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="analyze_data",
                    description="Perform basic data analysis on a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="execute_query",
                    description="Execute a SELECT SQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 100},
                        },
                        "required": ["connection_name", "query"],
                    },
                ),
                Tool(
                    name="find_correlations",
                    description="Find correlations between numeric columns in a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                        },
                        "required": ["connection_name", "table_name"],
                    },
                ),
                Tool(
                    name="detect_anomalies",
                    description="Detect anomalies in a numeric column using Z-score",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                            "column_name": {"type": "string"},
                        },
                        "required": ["connection_name", "table_name", "column_name"],
                    },
                ),
                Tool(
                    name="time_series_analysis",
                    description="Perform basic time series analysis on date and value columns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_name": {"type": "string"},
                            "table_name": {"type": "string"},
                            "date_column": {"type": "string"},
                            "value_column": {"type": "string"},
                        },
                        "required": ["connection_name", "table_name", "date_column", "value_column"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name in self.tools:
                    return await self.tools[name].execute(**arguments)
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Tool {name} error: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def async_main():
    logging.basicConfig(level=logging.INFO)
    server = PostgreSQLMCPServer()
    await server.run()


def main():
    """Entry point for poetry script"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
