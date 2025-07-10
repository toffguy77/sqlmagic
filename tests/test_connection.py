from unittest.mock import Mock, patch

import pytest

from sqlmagic.core.connection import ConnectionManager
from sqlmagic.core.exceptions import ConnectionError


@pytest.fixture
def connection_manager():
    return ConnectionManager(max_connections=2)


def test_connection_manager_connect(connection_manager):
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_pool.return_value = Mock()
        connection_manager.connect("test", "localhost", 5432, "db", "user", "pass")
        assert "test" in connection_manager.pools
        assert connection_manager.is_connected("test")


def test_connection_manager_disconnect(connection_manager):
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_pool.return_value = Mock()
        connection_manager.connect("test", "localhost", 5432, "db", "user", "pass")
        connection_manager.disconnect("test")
        assert "test" not in connection_manager.pools


def test_connection_manager_get_connection(connection_manager):
    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        mock_conn = Mock()
        mock_pool.return_value.getconn.return_value = mock_conn
        connection_manager.connect("test", "localhost", 5432, "db", "user", "pass")

        with connection_manager.get_connection("test") as conn:
            assert conn == mock_conn


def test_invalid_connection_params(connection_manager):
    with patch("psycopg2.pool.SimpleConnectionPool", side_effect=Exception("Invalid")):
        with pytest.raises(ConnectionError):
            connection_manager.connect("test", "invalid", 5432, "db", "user", "pass")


def test_connection_not_found(connection_manager):
    with pytest.raises(ConnectionError):
        with connection_manager.get_connection("nonexistent"):
            pass
