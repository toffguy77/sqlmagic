from unittest.mock import Mock, patch

import pytest

from sqlmagic.core.config import Config
from sqlmagic.core.connection import ConnectionManager
from sqlmagic.tools.basic import (
    AnalyzeDataTool,
    ConnectTool,
    DescribeTableTool,
    ExploreTablesTool,
    SampleDataTool,
)


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.fixture
def connect_tool(connection_manager, config):
    return ConnectTool(connection_manager, config)


@pytest.fixture
def explore_tool(connection_manager, config):
    return ExploreTablesTool(connection_manager, config)


@pytest.fixture
def describe_tool(connection_manager, config):
    return DescribeTableTool(connection_manager, config)


@pytest.fixture
def sample_tool(connection_manager, config):
    return SampleDataTool(connection_manager, config)


@pytest.fixture
def analyze_tool(connection_manager, config):
    return AnalyzeDataTool(connection_manager, config)


@pytest.mark.asyncio
async def test_connect_tool_success(connect_tool):
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_pool.return_value = Mock()
        result = await connect_tool.execute(
            "test", "localhost", "testdb", "user", "pass"
        )
        assert "Connected" in result[0].text


@pytest.mark.asyncio
async def test_connect_tool_failure(connect_tool):
    with patch(
        "psycopg2.pool.SimpleConnectionPool", side_effect=Exception("Connection failed")
    ):
        result = await connect_tool.execute(
            "test", "localhost", "testdb", "user", "pass"
        )
        assert "Connection failed" in result[0].text


@pytest.mark.asyncio
async def test_explore_tables(explore_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("users", "BASE TABLE"),
        ("orders", "BASE TABLE"),
    ]

    with patch.object(explore_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = mock_cursor
        explore_tool.connection_manager.pools = {"test": Mock()}

        result = await explore_tool.execute("test")
        assert "users" in result[0].text
        assert "orders" in result[0].text


@pytest.mark.asyncio
async def test_describe_table(describe_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("id", "integer", "NO"),
        ("name", "varchar", "YES"),
    ]

    with patch.object(describe_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = mock_cursor
        describe_tool.connection_manager.pools = {"test": Mock()}

        result = await describe_tool.execute("test", "users")
        assert "id: integer" in result[0].text
        assert "name: varchar" in result[0].text


@pytest.mark.asyncio
async def test_sample_data(sample_tool):
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
    ]

    with patch.object(sample_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        sample_tool.connection_manager.pools = {"test": Mock()}

        result = await sample_tool.execute("test", "users")
        assert "Sample from users" in result[0].text


@pytest.mark.asyncio
async def test_analyze_data(analyze_tool):
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [(100,), (5,)]  # count, columns

    with patch.object(analyze_tool.connection_manager, "get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = mock_cursor
        analyze_tool.connection_manager.pools = {"test": Mock()}

        result = await analyze_tool.execute("test", "users")
        assert "100 rows" in result[0].text
        assert "5 columns" in result[0].text
