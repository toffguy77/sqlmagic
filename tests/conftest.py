from unittest.mock import Mock

import pytest

from sqlmagic.core.config import Config
from sqlmagic.core.connection import ConnectionManager


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor
