# targets/agent_tools.py
import sqlite3

def execute_user_query(user_sql: str):
    """Vulnerable tool: Directly executes LLM-generated raw SQL."""
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    # Risk: LLM can execute DROP TABLE or SELECT * FROM users
    return cursor.executescript(user_sql)
