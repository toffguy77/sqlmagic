class SQLMagicError(Exception):
    """Base exception for SQLMagic"""
    pass

class ConnectionError(SQLMagicError):
    """Database connection error"""
    pass

class ValidationError(SQLMagicError):
    """Input validation error"""
    pass

class QueryError(SQLMagicError):
    """SQL query execution error"""
    pass