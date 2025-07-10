from unittest.mock import Mock, patch

import pytest
from mcp.types import TextContent

from sqlmagic.core.config import Config
from sqlmagic.core.connection import ConnectionManager
from sqlmagic.tools.analytics import (
    DetectAnomaliesTool,
    FindCorrelationsTool,
    TimeSeriesAnalysisTool,
)


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.fixture
def correlation_tool(connection_manager, config):
    return FindCorrelationsTool(connection_manager, config)


@pytest.fixture
def anomaly_tool(connection_manager, config):
    return DetectAnomaliesTool(connection_manager, config)


@pytest.fixture
def timeseries_tool(connection_manager, config):
    return TimeSeriesAnalysisTool(connection_manager, config)


@pytest.mark.asyncio
async def test_correlation_analysis(correlation_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.side_effect = [
        [("col1",), ("col2",)],  # numeric columns
        [(1, 2), (3, 4), (5, 6)],  # data
    ]

    with patch.object(
        correlation_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        correlation_tool.connection_manager.pools = {"test": Mock()}

        result = await correlation_tool.execute("test", "table")
        assert isinstance(result[0], TextContent)


@pytest.mark.asyncio
async def test_insufficient_numeric_columns(correlation_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [("col1",)]  # only one column

    with patch.object(
        correlation_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        correlation_tool.connection_manager.pools = {"test": Mock()}

        result = await correlation_tool.execute("test", "table")
        assert "Insufficient numeric columns" in result[0].text


@pytest.mark.asyncio
async def test_anomaly_detection(anomaly_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [(i,) for i in range(50)] + [
        (100,)
    ]  # more data + outlier

    with patch.object(anomaly_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        anomaly_tool.connection_manager.pools = {"test": Mock()}

        result = await anomaly_tool.execute("test", "table", "column")
        assert "Anomalies" in result[0].text


@pytest.mark.asyncio
async def test_insufficient_data_anomaly(anomaly_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [(1,), (2,)]  # too few points

    with patch.object(anomaly_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        anomaly_tool.connection_manager.pools = {"test": Mock()}

        result = await anomaly_tool.execute("test", "table", "column")
        assert "Insufficient data" in result[0].text


@pytest.mark.asyncio
async def test_time_series_analysis(timeseries_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("2023-01-01", 10),
        ("2023-01-02", 20),
        ("2023-01-03", 30),
    ]

    with patch.object(
        timeseries_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        timeseries_tool.connection_manager.pools = {"test": Mock()}

        result = await timeseries_tool.execute("test", "table", "date_col", "value_col")
        assert "Time series" in result[0].text
        assert "trend: increasing" in result[0].text
