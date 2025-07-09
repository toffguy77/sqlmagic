import pytest
from unittest.mock import Mock, patch
from src.sqlmagic.core.connection import ConnectionManager
from src.sqlmagic.core.config import Config
from src.sqlmagic.tools.basic import ConnectTool, ExploreTablesTool

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def connection_manager():
    return ConnectionManager()

@pytest.fixture
def connect_tool(connection_manager, config):
    return ConnectTool(connection_manager, config)

@pytest.mark.asyncio
async def test_connect_tool_success(connect_tool):
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = Mock()
        result = await connect_tool.execute("test", "localhost", "testdb", "user", "pass")
        assert "Connected" in result[0].text

@pytest.mark.asyncio
async def test_connect_tool_failure(connect_tool):
    with patch('psycopg2.connect', side_effect=Exception("Connection failed")):
        result = await connect_tool.execute("test", "localhost", "testdb", "user", "pass")
        assert "Connection failed" in result[0].text