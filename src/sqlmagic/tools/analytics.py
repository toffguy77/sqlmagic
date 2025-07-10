from typing import List

import numpy as np
import pandas as pd
from mcp.types import TextContent
from scipy import stats

from ..utils.validators import sanitize_sql_identifier
from .base import BaseTool


class FindCorrelationsTool(BaseTool):
    async def execute(self, connection_name: str, table_name: str) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        with self.connection_manager.get_connection(connection_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND data_type IN ('integer', 'bigint', 'numeric', 'real', 'double precision')",
                (table_name,),
            )
            numeric_cols = [row[0] for row in cursor.fetchall()]
            if len(numeric_cols) < 2:
                return [TextContent(type="text", text="Insufficient numeric columns")]

            cols_str = ", ".join(numeric_cols)
            cursor.execute(
                f"SELECT {cols_str} FROM {table_name} WHERE {' AND '.join([f'{col} IS NOT NULL' for col in numeric_cols])} LIMIT {self.config.max_rows_limit}"
            )
            data = cursor.fetchall()
            if not data:
                return [TextContent(type="text", text="No data available")]

            df = pd.DataFrame(data, columns=numeric_cols)
            corr = df.corr()
            result = "Strong correlations (>0.5):\n"
            found = False
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j and abs(corr.iloc[i, j]) > 0.5:
                        result += f"• {col1} - {col2}: {corr.iloc[i, j]:.3f}\n"
                        found = True
            if not found:
                result += "No strong correlations found"
            return [TextContent(type="text", text=result)]


class DetectAnomaliesTool(BaseTool):
    async def execute(
        self, connection_name: str, table_name: str, column_name: str
    ) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        column_name = sanitize_sql_identifier(column_name)
        with self.connection_manager.get_connection(connection_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT {self.config.max_rows_limit}"
            )
            values = [float(row[0]) for row in cursor.fetchall()]
            if len(values) < 10:
                return [
                    TextContent(
                        type="text", text="Insufficient data for anomaly detection"
                    )
                ]

            z_scores = np.abs(stats.zscore(values))
            anomalies = np.array(values)[z_scores > 3]
            return [
                TextContent(
                    type="text",
                    text=f"Anomalies in {column_name}: {len(anomalies)} detected (Z-score > 3)",
                )
            ]


class TimeSeriesAnalysisTool(BaseTool):
    async def execute(
        self, connection_name: str, table_name: str, date_column: str, value_column: str
    ) -> List[TextContent]:
        self.validate_connection(connection_name)
        table_name = sanitize_sql_identifier(table_name)
        date_column = sanitize_sql_identifier(date_column)
        value_column = sanitize_sql_identifier(value_column)
        with self.connection_manager.get_connection(connection_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {date_column}, {value_column} FROM {table_name} WHERE {date_column} IS NOT NULL AND {value_column} IS NOT NULL ORDER BY {date_column} LIMIT {self.config.max_rows_limit}"
            )
            data = cursor.fetchall()
            if len(data) < 2:
                return [
                    TextContent(
                        type="text", text="Insufficient data for time series analysis"
                    )
                ]

            df = pd.DataFrame(data, columns=[date_column, value_column])
            trend = (
                "increasing"
                if df[value_column].iloc[-1] > df[value_column].iloc[0]
                else "decreasing"
            )
            mean_val = df[value_column].mean()
            std_val = df[value_column].std()
            return [
                TextContent(
                    type="text",
                    text=f"Time series {value_column}: {len(data)} points, trend: {trend}, mean: {mean_val:.2f}, std: {std_val:.2f}",
                )
            ]
