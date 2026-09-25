import os
import time
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables FIRST before other imports
load_dotenv()

from modules.ingestion import ingest_data
from modules.vector_store import create_vector_db, load_existing_db
from modules.agent import create_rag_agent
from modules.evaluator import evaluate_performance

def main():
    # --- Configuration ---
    PDF_PATH = os.getenv("PDF_PATH", "data/default.pdf")
    DB_DIR = os.getenv("DB_DIR", "./chroma_db")
    
    # --- Step 1: Initialize or Load Database ---
    if not os.path.exists(DB_DIR):
        print("🚀 Initializing OWASP Security Knowledge Base (First time setup)...")
        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(
                f"❌ PDF file not found at '{PDF_PATH}'. "
                "Please place your OWASP LLM Top 10 PDF in the 'data/' folder."
            )
        pdf_docs = ingest_data(PDF_PATH)
        vector_db = create_vector_db(pdf_docs, DB_DIR)
        print("✅ Database created and persisted.")
        
        print(f"Total Pages Loaded: {len(pdf_docs)}")
        print(f"Sample Page 1 Content:\n{pdf_docs[0].page_content[:300]}")
    else:
        print("📚 Loading existing OWASP Security Knowledge Base...")
        vector_db = load_existing_db(DB_DIR)

    # --- Step 2: Initialize the Agentic System ---
    # We pass vector_db so tools can search security guidelines
    agent_executor = create_rag_agent(vector_db)

   # --- Step 3: Software Engineering Security Tasks ---
    agent_tasks = [
        # Task 1: Audit code and write patched code
        (
            "Inspect my local 'bot.py' file. Search ChromaDB for OWASP rules on "
            "LLM01 (Prompt Injection) and LLM02 (Insecure Output Handling / Disclosure). "
            "Identify vulnerabilities in bot.py, explain why they are risky, and save a "
            "refactored, secure version named 'bot_fixed.py' in the outputs folder."
        ),
        # Task 2: Audit configuration text and write markdown report
        (
            "Inspect my local 'system_prompt.txt' file. Search ChromaDB for OWASP rules on "
            "System Prompt Leakage and Sensitive Information Disclosure. "
            "Identify security risks in the configuration and write a detailed audit report "
            "named 'prompt_audit.md' in the outputs folder."
        )
    ]

    print("\n--- Starting OWASP Security Agent Workflow ---")
    for i, task in enumerate(agent_tasks, 1):
        print(f"\n[Task {i}]: {task}")
        
        # Modern way for create_agent / LangGraph state
        result = agent_executor.invoke({"messages": [("human", task)]})
        final_answer = result["messages"][-1].content
        
        print(f"\n🤖 Agent Final Answer:\n{final_answer}")
        
        # Reflection & Evaluation (Self-Audit)
        print("\n🧐 Auditor Reflection:")
        audit_results = evaluate_performance(task, final_answer)
        print(audit_results)
        print("-" * 60)

if __name__ == "__main__":
    # --- Start Timer ---
    start_time = time.time()
    print(f"🕒 System Start: {time.strftime('%H:%M:%S')}")

    main()

    # --- End Timer ---
    end_time = time.time()
    total_duration = end_time - start_time
    print("\n" + "="*50)
    print(f"🏁 System Finished: {time.strftime('%H:%M:%S')}")
    print(f"⏱️ Total Execution Time: {str(timedelta(seconds=round(total_duration)))} (H:MM:SS)")
    print("="*50)
