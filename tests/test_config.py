import os
from unittest.mock import patch

import pytest

from sqlmagic.core.config import Config


def test_config_defaults():
    config = Config()
    assert config.log_level == "INFO"
    assert config.max_connections == 10
    assert config.query_timeout == 30
    assert config.max_rows_limit == 10000


def test_config_from_env():
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "MAX_CONNECTIONS": "20",
        "QUERY_TIMEOUT": "60",
        "MAX_ROWS_LIMIT": "5000",
    }
    with patch.dict(os.environ, env_vars):
        config = Config.from_env()
        assert config.log_level == "DEBUG"
        assert config.max_connections == 20
        assert config.query_timeout == 60
        assert config.max_rows_limit == 5000


def test_config_invalid_values():
    with patch.dict(os.environ, {"MAX_CONNECTIONS": "invalid"}):
        with pytest.raises(ValueError):
            Config.from_env()
