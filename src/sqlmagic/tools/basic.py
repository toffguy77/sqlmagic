import pandas as pd
from psycopg2.extras import RealDictCursor
from mcp.types import TextContent
from .base import BaseTool
from ..utils.validators import sanitize_sql_identifier
from ..core.exceptions import ValidationError, QueryError

class ConnectTool(BaseTool):
    async def execute(self, connection_name: str, host: str, database: str, username: str, password: str, port: int = 5432) -> List[TextContent]:
        try:
            self.connection_manager.connect(connection_name, host, port, database, username, password)
            return [TextContent(type="text", text=f"Connected to {database} as {connection_name}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Connection failed: {str(e)}")]

class ExploreTablesTool(BaseTool):
    async def execute(self, connection_name: str) -> List[TextContent]:
        self.validate_connection(connection_name)
        conn = self.connection_manager.get_connection(connection_name)
        cursor = conn.cursor()
        cursor.execute("SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = cursor.fetchall()
        result = "Tables:\n" + "\n".join([f"• {name} ({type_})" for name, type_ in tables])
        return [TextContent(type="text", text=result)]

class DescribeTableTool(BaseTool):
    async def execute(self, connection_name: str, table_name: str) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        conn = self.connection_manager.get_connection(connection_name)
        cursor = conn.cursor()
        cursor.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", (table_name,))
        columns = cursor.fetchall()
        result = f"Structure of {table_name}:\n" + "\n".join([f"• {col}: {dtype} {'NULL' if null == 'YES' else 'NOT NULL'}" for col, dtype, null in columns])
        return [TextContent(type="text", text=result)]

class SampleDataTool(BaseTool):
    async def execute(self, connection_name: str, table_name: str, limit: int = 10) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        limit = min(limit, self.config.max_rows_limit)
        with self.connection_manager.get_connection(connection_name) as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
            rows = cursor.fetchall()
            if not rows:
                return [TextContent(type="text", text="No data found")]
            df = pd.DataFrame(rows)
            return [TextContent(type="text", text=f"Sample from {table_name} ({len(rows)} rows):\n{df.to_string(index=False)}")]

class AnalyzeDataTool(BaseTool):
    async def execute(self, connection_name: str, table_name: str) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        conn = self.connection_manager.get_connection(connection_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = %s", (table_name,))
        cols = cursor.fetchone()[0]
        return [TextContent(type="text", text=f"Analysis of {table_name}: {count:,} rows, {cols} columns")]