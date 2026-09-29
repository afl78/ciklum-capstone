import os
from langchain.tools import tool
from modules.generator import query_chatbot

def get_tools(vector_db, run_timestamp: str, attempt: int = 1):

    @tool
    def search_owasp_security_rules(query: str):
        """Consult this tool to search OWASP Top 10 for LLM Applications security rules,
        vulnerability codes (LLM01, LLM02, etc.), risk definitions, and remediation patterns."""
        response = query_chatbot(vector_db, query)
        return response.get('answer', "No relevant security guidelines found in knowledge base.")

    @tool
    def read_local_file(file_path: str):
        """Action: Reads and returns the raw text content of a local file for security auditing."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading target file '{file_path}': {str(e)}"

    @tool
    def write_output_file(content: str, filename: str):
        """Action: Saves generated security outputs directly into the 'outputs' folder 
        prefixed with execution session timestamp and suffixed with the attempt version."""
        os.makedirs("outputs", exist_ok=True)
        
        # Split filename to insert the attempt version suffix before extension
        # e.g., 'bot_fixed.py' -> name='bot_fixed', ext='.py'
        name, ext = os.path.splitext(filename)
        
        # Output format: outputs/20260925_143005_bot_fixed_v1.py
        versioned_filename = f"{run_timestamp}_{name}_v{attempt}{ext}"
        
        path = os.path.join("outputs", versioned_filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully saved to {path}"

    return [search_owasp_security_rules, read_local_file, write_output_file]