import os
from langchain.tools import tool
from modules.generator import query_chatbot

def get_tools(vector_db):
    """
    Creates and returns the tool set for the Security Auditor agent.
    Tools are closure-bound to access the local vector_db instance.
    """

    @tool
    def search_owasp_security_rules(query: str):
        """Consult this tool to search OWASP Top 10 for LLM Applications security rules,
        vulnerability codes (LLM01, LLM02, etc.), risk definitions, and remediation patterns."""
        response = query_chatbot(vector_db, query)
        return response.get('answer', "No relevant security guidelines found in knowledge base.")

    @tool
    def read_local_file(file_path: str):
        """Action: Reads and returns the raw text content of a local file (e.g., Python scripts,
        configuration files, or system prompt files) for security auditing."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading target file '{file_path}': {str(e)}"

    @tool
    def write_output_file(content: str, filename: str):
        """Action: Saves generated security outputs (patched code files, markdown security reports,
        or audit tickets) directly into the 'outputs' folder."""
        os.makedirs("outputs", exist_ok=True)
        path = os.path.join("outputs", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully saved to {path}"

    return [search_owasp_security_rules, read_local_file, write_output_file]