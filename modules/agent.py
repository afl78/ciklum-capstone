from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import get_tools

def create_rag_agent(vector_db):
    # 1. Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", 
        temperature=0
    )
    
    # 2. Load domain-specific security tools
    tools = get_tools(vector_db)
    
    # 3. Security Auditor System Persona
    system_prompt = (
        "You are an expert Application Security Engineer specializing in AI/LLM vulnerability auditing.\n\n"
        "Your goal is to inspect source code, system prompts, and configuration files against the OWASP Top 10 for LLM Applications.\n\n"
        "Follow these execution guidelines:\n"
        "1. Read Local Files: Always use the file inspection tool first to examine target code or text files.\n"
        "2. Consult Knowledge Base: Query ChromaDB for specific OWASP security definitions, vulnerability codes (e.g., LLM01, LLM02), and remediation patterns.\n"
        "3. Reflect & Diagnose: Compare the local code against the retrieved security rules. Identify exact lines or logic causing the risk.\n"
        "4. Produce Output: Use the file output tool to save fixed code files, security reports, or patch files to the 'outputs' directory as instructed."
    )

    # 4. Construct the agent graph runner
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent

# def create_rag_agent(vector_db):
#     # The 'Reasoning Engine'
#     llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    
#     tools = get_tools(vector_db)
    
#     # The 'System Instruction' for Reflection and Reasoning
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", (
#             "You are an expert AI Research Agent. "
#             "1. REASON: Analyze the user's request. Do you need to search the lecture notes? "
#             "2. ACT: Use the search tool to find technical facts. "
#             "3. REFLECT: Look at your answer. Does it fully answer the user? "
#             "If not, search again with a better query. "
#             "4. REPORT: If asked to save, use the write_summary_report tool."
#         )),
#         MessagesPlaceholder(variable_name="chat_history", optional=True),
#         ("human", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ])

#     # Construct the Agent
#     agent = create_tool_calling_agent(llm, tools, prompt)
    
#     # The Executor handles the loop (Max 5 iterations to avoid infinite loops)
#     return AgentExecutor(
#         agent=agent, 
#         tools=tools, 
#         verbose=True, 
#         max_iterations=5,
#         handle_parsing_errors=True
#     )