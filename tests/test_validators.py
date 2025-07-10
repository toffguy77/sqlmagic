import pytest

from sqlmagic.utils.validators import QueryValidator, sanitize_sql_identifier


def test_sql_injection_detection():
    dangerous_queries = [
        "DROP TABLE users",
        "DELETE FROM users",
        "TRUNCATE TABLE logs",
        "ALTER TABLE users ADD COLUMN",
        "CREATE USER hacker",
        "GRANT ALL ON users TO hacker",
    ]
    for query in dangerous_queries:
        assert not QueryValidator.is_safe_query(query)


def test_safe_queries():
    safe_queries = [
        "SELECT * FROM users",
        "SELECT COUNT(*) FROM orders",
        "SELECT name, email FROM customers WHERE id = 1",
    ]
    for query in safe_queries:
        assert QueryValidator.is_safe_query(query)


def test_identifier_validation():
    valid_identifiers = ["users", "user_table", "_private", "table123"]
    invalid_identifiers = ["123table", "user-table", "user table", "user;table"]

    for identifier in valid_identifiers:
        assert QueryValidator.validate_identifier(identifier)

    for identifier in invalid_identifiers:
        assert not QueryValidator.validate_identifier(identifier)


def test_sanitize_sql_identifier():
    assert sanitize_sql_identifier("users") == "users"

    with pytest.raises(ValueError):
        sanitize_sql_identifier("123invalid")

    with pytest.raises(ValueError):
        sanitize_sql_identifier("user;drop")
