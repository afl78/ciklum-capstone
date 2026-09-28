from langchain_community.document_loaders import PyPDFLoader

def ingest_data(pdf_path):
    # 1. Process PDF
    pdf_loader = PyPDFLoader(pdf_path)
    pdf_docs = pdf_loader.load()
    
    return pdf_docs