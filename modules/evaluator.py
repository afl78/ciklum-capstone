import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def evaluate_performance(task_prompt: str, agent_output: str):
    """Evaluates agent output against task prompt and explicit OWASP security rubrics."""
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GOOGLE_API_KEY")

    evaluator_llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        max_retries=5
    )

    eval_template = PromptTemplate.from_template("""
You are a Principal Application Security Auditor evaluating an AI Security Agent's response.

SECURITY TASK:
{task_prompt}

AGENT RESPONSE:
{agent_output}

EVALUATION RUBRIC:
1. Vulnerability Accuracy: Did the agent correctly identify the OWASP Top 10 for LLM risk categories (e.g., LLM01, LLM02) relevant to the target?
2. Remediation Quality: Are the proposed code or configuration fixes concrete, secure, and production-ready?
3. Action Completion: Did the agent state that it inspected the local file, searched security rules, and saved output files as requested?

DECISION CRITERIA:
- Mark STATUS as PASSED only if all 3 criteria are fully satisfied and output files are created/refactored properly.
- Mark STATUS as NEEDS_REVISION if any criteria fail or if output generation was skipped.

Provide your evaluation in this EXACT format:
STATUS: [PASSED or NEEDS_REVISION]
SCORE: [X/10]
IDENTIFIED_RISKS: [List identified OWASP codes or 'None']
CRITIQUE: <Provide direct, actionable instructions on what is missing or wrong so the agent can fix it on the next turn. If PASSED, write 'No issues found.'>
""")

    formatted_prompt = eval_template.format(
        task_prompt=task_prompt,
        agent_output=agent_output
    )

    res = evaluator_llm.invoke(formatted_prompt)
    
    # Safely unpack string content whether res.content is str or list
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

    # Normalize text safely
    normalized_response = response_text.upper().replace("*", "").replace("[", "").replace("]", "")
    is_passed = "STATUS: PASSED" in normalized_response

    return {
        "is_passed": is_passed,
        "feedback": response_text
    }