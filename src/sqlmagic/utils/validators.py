import re


class QueryValidator:
    DANGEROUS_PATTERNS = [
        r"\bDROP\s+TABLE\b",
        r"\bDELETE\s+FROM\b",
        r"\bTRUNCATE\b",
        r"\bALTER\s+TABLE\b",
        r"\bCREATE\s+USER\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
    ]

    @classmethod
    def is_safe_query(cls, query: str) -> bool:
        query_upper = query.upper()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper):
                return False
        return True

    @classmethod
    def validate_identifier(cls, name: str) -> bool:
        return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))


def sanitize_sql_identifier(identifier: str) -> str:
    if not QueryValidator.validate_identifier(identifier):
        raise ValueError(f"Invalid identifier: {identifier}")
    return identifier
