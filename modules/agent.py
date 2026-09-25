import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import get_tools

def create_rag_agent(vector_db):
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    api_key = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        max_retries=5
    )
    
    tools = get_tools(vector_db)
    
    # Load externalized System Persona Prompt
    prompt_path = os.path.join("prompts", "security_auditor.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are an expert AI Security Auditor."

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )