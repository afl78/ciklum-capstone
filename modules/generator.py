import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

def query_chatbot(vector_db, question):
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        google_api_key=api_key,
        temperature=0
    )

    # 1. Security-Focused System Prompt
    system_prompt = (
        "You are an expert Application Security Assistant specializing in LLM application security. "
        "Use the provided OWASP Top 10 security context to answer queries accurately. "
        "Cite vulnerability categories (e.g., LLM01, LLM02), risks, and mitigations when available. "
        "If the answer is not present in the provided context, state clearly that the "
        "knowledge base does not contain that specific rule."
        "\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 2. RAG Chains Setup
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(vector_db.as_retriever(), question_answer_chain)

    # 3. Execution
    return rag_chain.invoke({"input": question})