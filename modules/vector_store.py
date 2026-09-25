import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def create_vector_db(pdf_docs, db_dir):
    """
    Chunks the input data, embeds it, and saves it to a local directory.
    """
    # 1. Initialize the splitter (using tiktoken for OpenAI compatibility)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=1000,
        chunk_overlap=100
    )
    
    # 2. Split PDF documents
    pdf_chunks = text_splitter.split_documents(pdf_docs)    
    
    all_chunks = pdf_chunks
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create and Persist the Vector Store
    vector_db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=db_dir
    )
    
    return vector_db

def load_existing_db(db_dir):
    """
    Loads an existing Chroma database from the disk.
    """
    if not os.path.exists(db_dir):
        raise FileNotFoundError(f"No vector database found at {db_dir}. Please run the ingestion first.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # In modern LangChain-Chroma, you simply initialize the object with the directory
    vector_db = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings
    )
    
    return vector_db