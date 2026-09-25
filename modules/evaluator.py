import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

def evaluate_performance(question, answer):
    """
    An independent LLM pass that acts as a Security Critic/Auditor.
    Evaluates agent output against security rules and task requirements.
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    api_key = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        google_api_key=api_key,
        temperature=0
    )
    
    eval_prompt = ChatPromptTemplate.from_template("""
    You are a Senior Application Security Auditor evaluating an AI Security Agent's response.
    
    SECURITY TASK: {question}
    AGENT_RESPONSE: {answer}
    
    EVALUATION CRITERIA:
    1. Vulnerability Accuracy: Did the agent correctly identify the OWASP risk category (e.g., LLM01, LLM02) and explain why the file was insecure?
    2. Remediation Quality: Did the agent provide clear, actionable, and secure code or configuration fixes?
    3. Action Completion: Did the agent follow instructions regarding reading files, searching security rules, or saving output files?
    
    Provide your response in the following format:
    - Score: [X/10]
    - Identified OWASP Risk: [Name/Code or "None"]
    - Actionable Feedback: [One or two sentences on how the response or security analysis could be improved]
    """)
    
    chain = eval_prompt | llm
    result = chain.invoke({"question": question, "answer": answer})

    # Handle structured content output from Gemini
    if isinstance(result.content, list):
        return result.content[0].get('text', str(result.content))
    return result.content