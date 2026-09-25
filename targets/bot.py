import sqlite3
from google import genai

client = genai.Client()

def handle_user_request(user_input: str):
    # Unsanitized prompt passed directly
    prompt = f"You are a database assistant. User input: {user_input}"
    response = client.models.generate_content(model='gemini-3.1-flash-lite', contents=prompt)

    # Executing raw LLM output against DB directly
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.executescript(response.text)
    return "Success"