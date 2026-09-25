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
    os.makedirs("logs", exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{run_timestamp}_execution_log.txt"
    
    logger = ConsoleLogger(log_filename)
    sys.stdout = logger

    # Load configurable retry limit
    max_retries = int(os.getenv("MAX_AUDIT_RETRIES", 3))

    print(f"🕒 System Start: {time.strftime('%H:%M:%S')} (Session ID: {run_timestamp})")
    print(f"📝 Logging session output to: {log_filename}")
    print(f"🔄 Max Configured Retries per Task: {max_retries}\n")

    try:
        PDF_PATH = os.getenv("PDF_PATH", "data/OWASP_LLM_Top_10.pdf")
        DB_DIR = os.getenv("DB_DIR", "./chroma_db")
        
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

        agent_executor = create_rag_agent(vector_db, run_timestamp)
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
            
            # Maintain active conversation state across retries
            conversation_messages = [("human", task_prompt)]
            attempt = 1

            while attempt <= max_retries:
                print(f"\n🔄 [Execution Attempt {attempt}/{max_retries}]:")
                
                # Instantiate agent executor dynamically with current attempt version
                agent_executor = create_rag_agent(vector_db, run_timestamp, attempt)
                
                # Execute Agent Graph
                result = agent_executor.invoke({"messages": conversation_messages})
                log_agent_execution_stream(result)
                
                final_answer = result["messages"][-1].content
                print(f"\n🤖 [Agent Final Output (Attempt {attempt})]:\n{final_answer}")
                
                # Evaluator Pass
                print("\n🧐 [Auditor Reflection Pass]:")
                eval_result = evaluate_performance(task_prompt, final_answer)
                print(eval_result["feedback"])
                
                if eval_result["is_passed"]:
                    print(f"\n✅ Task passed security audit on attempt {attempt}!")
                    break
                
                if attempt < max_retries:
                    print(f"\n⚠️ Audit feedback requires improvement. Re-injecting critique into agent instructions for Attempt {attempt + 1}...")
                    
                    critique_prompt = (
                        f"Your previous attempt was evaluated and requires improvement.\n\n"
                        f"AUDITOR CRITIQUE & INSTRUCTIONS:\n{eval_result['feedback']}\n\n"
                        f"Please re-examine the target files, consult ChromaDB rules if necessary, rewrite/save updated outputs, and address all feedback points."
                    )
                    
                    conversation_messages.append(("assistant", final_answer))
                    conversation_messages.append(("human", critique_prompt))
                else:
                    print(f"\n❌ Reached maximum retries ({max_retries}). Continuing to next task.")
                
                attempt += 1

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