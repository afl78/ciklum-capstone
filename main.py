import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from modules import (
    ingest_data,
    create_vector_db,
    load_existing_db,
    create_rag_agent,
    evaluate_performance,
    ConsoleLogger,
    load_tasks,
    log_agent_execution_stream
)

def main():
    # 1. Initialize Logging Session
    os.makedirs("logs", exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{run_timestamp}_execution_log.txt"
    
    logger = ConsoleLogger(log_filename)
    sys.stdout = logger

    print(f"🕒 System Start: {time.strftime('%H:%M:%S')} (Session ID: {run_timestamp})")
    print(f"📝 Logging session output to: {log_filename}\n")

    try:
        PDF_PATH = os.getenv("PDF_PATH", "data/OWASP_LLM_Top_10.pdf")
        DB_DIR = os.getenv("DB_DIR", "./chroma_db")
        
        # 2. Initialize or Load Security Knowledge Base
        if not os.path.exists(DB_DIR):
            print("🚀 Initializing OWASP Security Knowledge Base (First time setup)...")
            if not os.path.exists(PDF_PATH):
                raise FileNotFoundError(f"❌ PDF file not found at '{PDF_PATH}'.")
            pdf_docs = ingest_data(PDF_PATH)
            vector_db = create_vector_db(pdf_docs, DB_DIR)
            print("✅ Database created and persisted.")
        else:
            print("📚 Loading existing OWASP Security Knowledge Base...")
            vector_db = load_existing_db(DB_DIR)

        # 3. Instantiate Agent System with Session Timestamp
        agent_executor = create_rag_agent(vector_db, run_timestamp)

        # 4. Load System Tasks
        tasks = load_tasks("config/tasks.json")

        print("\n==================================================")
        print("      🛡️  OWASP SECURITY AUDITOR AGENT WORKFLOW    ")
        print("==================================================")

        for i, task_item in enumerate(tasks, 1):
            task_id = task_item.get("id", f"TASK_{i}")
            task_name = task_item.get("name", "Security Task")
            task_prompt = task_item.get("prompt")

            print(f"\n--------------------------------------------------")
            print(f"📋 [{task_id}]: {task_name}")
            print(f"📝 [Task Prompt]: {task_prompt}")
            print(f"--------------------------------------------------")
            
            # Execute Agent Graph Loop
            result = agent_executor.invoke({"messages": [("human", task_prompt)]})
            
            # Print Real-Time Tool Execution Logs
            log_agent_execution_stream(result)
            
            # Print Final LLM Answer
            final_answer = result["messages"][-1].content
            print(f"\n🤖 [Agent Final Output]:\n{final_answer}")
            
            # Reflection & Evaluation Pass
            print("\n🧐 [Auditor Reflection Pass]:")
            audit_results = evaluate_performance(task_prompt, final_answer)
            print(audit_results)
            print("=" * 50)

    finally:
        print(f"\n📁 Log session complete. File saved to: {log_filename}")
        sys.stdout = logger.terminal
        logger.close()

if __name__ == "__main__":
    start_time = time.time()
    
    main()

    end_time = time.time()
    total_duration = end_time - start_time
    print("\n" + "="*50)
    print(f"🏁 System Finished: {time.strftime('%H:%M:%S')}")
    print(f"⏱️ Total Execution Time: {str(timedelta(seconds=round(total_duration)))} (H:MM:SS)")
    print("="*50)