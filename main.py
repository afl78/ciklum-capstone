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
    log_agent_execution_stream,
    load_critique_prompt
)


def init_logging():
    """Initializes timestamped logging session and redirects sys.stdout."""
    os.makedirs("logs", exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{run_timestamp}_execution_log.txt"
    
    logger = ConsoleLogger(log_filename)
    sys.stdout = logger

    print(f"🕒 System Start: {time.strftime('%H:%M:%S')} (Session ID: {run_timestamp})")
    print(f"📝 Logging session output to: {log_filename}\n")
    
    return logger, log_filename, run_timestamp


def load_pipeline_config():
    """Loads system execution settings from environment variables."""
    pdf_path = os.getenv("PDF_PATH", "data/OWASP_LLM_Top_10.pdf")
    db_dir = os.getenv("DB_DIR", "./chroma_db")
    max_retries = int(os.getenv("MAX_AUDIT_RETRIES", 3))

    print(f"⚙️ Config Loaded | PDF Path: '{pdf_path}' | DB Dir: '{db_dir}' | Max Retries: {max_retries}\n")
    return pdf_path, db_dir, max_retries


def get_or_create_vector_db(pdf_path: str, db_dir: str):
    """Initializes ChromaDB vector store if missing, otherwise loads existing database."""
    if not os.path.exists(db_dir):
        print("🚀 Initializing OWASP Security Knowledge Base (First time setup)...")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"❌ PDF file not found at '{pdf_path}'.")
        pdf_docs = ingest_data(pdf_path)
        vector_db = create_vector_db(pdf_docs, db_dir)
        print("✅ Database created and persisted.")
    else:
        print("📚 Loading existing OWASP Security Knowledge Base...")
        vector_db = load_existing_db(db_dir)
        
    return vector_db


def execute_task_retry_loop(vector_db, task_prompt, run_timestamp, max_retries):
    """Executes the agent workflow and evaluator reflection loop for a single task."""
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
            
            raw_critique_template = load_critique_prompt("prompts/critique_prompt.txt")
            critique_prompt = raw_critique_template.format(feedback=eval_result['feedback'])
            
            conversation_messages.append(("assistant", final_answer))
            conversation_messages.append(("human", critique_prompt))
        else:
            print(f"\n❌ Reached maximum retries ({max_retries}). Continuing to next task.")
        
        attempt += 1


def main():
    logger, log_filename, run_timestamp = init_logging()

    try:
        # Load environment config together (PDF, DB, and Retries)
        pdf_path, db_dir, max_retries = load_pipeline_config()

        # Load Knowledge Base & Tasks
        vector_db = get_or_create_vector_db(pdf_path, db_dir)
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
            
            execute_task_retry_loop(vector_db, task_prompt, run_timestamp, max_retries)

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
    print("\n" + "=" * 50)
    print(f"🏁 System Finished: {time.strftime('%H:%M:%S')}")
    print(f"⏱️ Total Execution Time: {str(timedelta(seconds=round(total_duration)))} (H:MM:SS)")
    print("=" * 50)