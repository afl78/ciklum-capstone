import sqlite3
from google import genai
import re

client = genai.Client()

def handle_user_request(user_input: str):
    # LLM01: Prompt Injection Mitigation
    # Use a system prompt to define strict boundaries and instruct the model to return structured data
    # rather than raw executable code.
    system_instruction = (
        "You are a database assistant. You must ONLY return a valid SQL SELECT statement "
        "that queries the 'users' table. Do not return any other text, explanations, or "
        "commands like DROP, DELETE, or UPDATE. If the request is unsafe, return 'ERROR'."
    )
    
    prompt = f"User request: {user_input}"
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite', 
        contents=prompt,
        config={"system_instruction": system_instruction}
    )
    
    sql_query = response.text.strip()

    # LLM05: Improper Output Handling Mitigation
    # 1. Validate the output: Ensure it is a safe SELECT statement
    if not re.match(r"^SELECT\s+[\w\s,]+\s+FROM\s+users(\s+WHERE\s+[\w\s='\"-]+)?$", sql_query, re.IGNORECASE):
        return "Error: Unsafe or invalid query generated."

    # 2. Use parameterized queries if possible (though here we are executing the LLM's query)
    # In a real-world scenario, never let the LLM write the SQL. 
    # Instead, have the LLM extract parameters and use a predefined query template.
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return str(results)
    except Exception as e:
        return f"Database error: {str(e)}"
