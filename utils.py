import re

# SQL keywords that indicate operations other than read-only
RESTRICTED_SQL_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'COPY', 'MERGE'
]

def is_valid_sql_query(sql: str) -> bool:
    """
    Returns True if the SQL is likely safe and read-only.
    Checks:
      - Only one statement
      - Starts with SELECT
      - No dangerous keywords
    """
    sql = sql.strip()

    # 1. Check single statement (allow trailing semicolon)
    statements = [s for s in sql.split(';') if s.strip()]
    if len(statements) != 1:
        return False

    # 2. Check starts with SELECT
    if not re.match(r'^\s*SELECT\b', sql, re.IGNORECASE):
        return False

    # 3. Check for dangerous keywords anywhere
    pattern = re.compile(r'\b(' + '|'.join(RESTRICTED_SQL_KEYWORDS) + r')\b', re.IGNORECASE)
    if pattern.search(sql):
        return False

    return True
