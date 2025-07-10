import time
from unittest.mock import Mock, patch

import pytest

from sqlmagic.core.config import Config
from sqlmagic.core.connection import ConnectionManager
from sqlmagic.tools.analytics import FindCorrelationsTool


@pytest.fixture
def config():
    config = Config()
    config.max_rows_limit = 1000
    config.query_timeout = 5
    return config


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.fixture
def correlation_tool(connection_manager, config):
    return FindCorrelationsTool(connection_manager, config)


@pytest.mark.asyncio
async def test_large_dataset_handling(correlation_tool):
    """Test handling of large datasets within limits"""
    mock_cursor = Mock()
    mock_cursor.fetchall.side_effect = [
        [("col1",), ("col2",)],  # columns
        [(i, i * 2) for i in range(1000)],  # max limit data
    ]

    with patch.object(
        correlation_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        correlation_tool.connection_manager.pools = {"test": Mock()}

        start_time = time.time()
        result = await correlation_tool.execute("test", "large_table")
        execution_time = time.time() - start_time

        assert execution_time < 10  # Should complete within reasonable time
        assert len(result) > 0


@pytest.mark.asyncio
async def test_query_timeout_simulation(correlation_tool):
    """Test query timeout handling"""

    def slow_fetchall_cols():
        time.sleep(0.1)  # Simulate slow query
        return [("col1",), ("col2",)]

    def slow_fetchall_data():
        return [(1, 2), (3, 4)]

    mock_cursor = Mock()
    mock_cursor.fetchall.side_effect = [slow_fetchall_cols(), slow_fetchall_data()]

    with patch.object(
        correlation_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        correlation_tool.connection_manager.pools = {"test": Mock()}

        # Should handle the delay gracefully
        result = await correlation_tool.execute("test", "table")
        assert len(result) > 0


@pytest.mark.asyncio
async def test_memory_usage_large_result(correlation_tool):
    """Test memory efficiency with large results"""
    mock_cursor = Mock()
    # Simulate large dataset
    large_data = [(i, i * 2, i * 3) for i in range(5000)]
    mock_cursor.fetchall.side_effect = [
        [("col1",), ("col2",), ("col3",)],
        large_data[:1000],  # Limited by max_rows_limit
    ]

    with patch.object(
        correlation_tool.connection_manager, "get_connection"
    ) as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        correlation_tool.connection_manager.pools = {"test": Mock()}

        result = await correlation_tool.execute("test", "table")
        # Should complete without memory issues
        assert isinstance(result[0].text, str)
        assert len(result[0].text) < 10000  # Reasonable output size
