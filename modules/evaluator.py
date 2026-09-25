import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def load_evaluator_prompt(prompt_path: str = "prompts/evaluator_prompt.txt") -> str:
    """Reads the evaluator prompt template from external config file with fallback protection."""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # Fallback template if file is not found
    return (
        "You are a Security Auditor.\n\n"
        "TASK:\n{task_prompt}\n\n"
        "RESPONSE:\n{agent_output}\n\n"
        "Provide your evaluation in format:\n"
        "STATUS: [PASSED or NEEDS_REVISION]\n"
        "CRITIQUE: <feedback>"
    )

def evaluate_performance(task_prompt: str, agent_output: str):
    """Evaluates agent output against task prompt using externalized evaluation template."""
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GOOGLE_API_KEY")

    evaluator_llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        max_retries=5
    )

    # 1. Load prompt template string from external file
    raw_template_string = load_evaluator_prompt("prompts/evaluator_prompt.txt")
    eval_template = PromptTemplate.from_template(raw_template_string)

    # 2. Format variables into prompt template
    formatted_prompt = eval_template.format(
        task_prompt=task_prompt,
        agent_output=agent_output
    )

    # 3. Invoke evaluator LLM
    res = evaluator_llm.invoke(formatted_prompt)
    
    # 4. Safely extract string content
    raw_content = res.content
    if isinstance(raw_content, list):
        text_blocks = []
        for block in raw_content:
            if isinstance(block, str):
                text_blocks.append(block)
            elif isinstance(block, dict) and "text" in block:
                text_blocks.append(block["text"])
            elif hasattr(block, "text"):
                text_blocks.append(getattr(block, "text"))
            else:
                text_blocks.append(str(block))
        response_text = "\n".join(text_blocks)
    else:
        response_text = str(raw_content)

    # 5. Normalize text and parse evaluation status
    normalized_response = response_text.upper().replace("*", "").replace("[", "").replace("]", "")
    is_passed = "STATUS: PASSED" in normalized_response

    return {
        "is_passed": is_passed,
        "feedback": response_text
    }