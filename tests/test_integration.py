from unittest.mock import Mock, patch

import pytest

from sqlmagic.core.config import Config
from sqlmagic.core.connection import ConnectionManager
from sqlmagic.tools.basic import ConnectTool, ExploreTablesTool


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


@pytest.mark.asyncio
async def test_full_workflow(connect_tool, explore_tool):
    """Test complete workflow: connect -> explore tables"""
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("users", "BASE TABLE"),
            ("orders", "BASE TABLE"),
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.return_value.getconn.return_value = mock_conn

        # Connect
        result = await connect_tool.execute(
            "test", "localhost", 5432, "db", "user", "pass"
        )
        assert "Connected" in result[0].text

        # Mock get_connection for explore
        with patch.object(
            explore_tool.connection_manager, "get_connection"
        ) as mock_get_conn:
            mock_get_conn.return_value.cursor.return_value = mock_cursor
            result = await explore_tool.execute("test")
            assert "users" in result[0].text
            assert "orders" in result[0].text


@pytest.mark.asyncio
async def test_database_operations_error_handling(explore_tool):
    """Test error handling in database operations"""
    with patch.object(
        explore_tool.connection_manager, "is_connected", return_value=True
    ):
        with patch.object(
            explore_tool.connection_manager, "get_connection"
        ) as mock_conn:
            mock_conn.side_effect = Exception("Database error")
            explore_tool.connection_manager.pools = {"test": Mock()}

            try:
                result = await explore_tool.execute("test")
                assert "error" in result[0].text.lower()
            except Exception as e:
                assert "Database error" in str(e)


@pytest.mark.asyncio
async def test_connection_validation(explore_tool):
    """Test connection validation before operations"""
    with pytest.raises(Exception):
        await explore_tool.execute("nonexistent_connection")
