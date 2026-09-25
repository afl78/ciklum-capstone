# from langchain_community.document_loaders import PyPDFium2Loader

# def ingest_data(pdf_path):
#     # Process PDF using PyPDFium2
#     pdf_loader = PyPDFium2Loader(pdf_path)
#     pdf_docs = pdf_loader.load()

#     return pdf_docs


# from langchain_community.document_loaders import PyMuPDFLoader

# def ingest_data(pdf_path):
#     # Process PDF using PyMuPDF instead of PyPDFLoader
#     pdf_loader = PyMuPDFLoader(pdf_path)
#     pdf_docs = pdf_loader.load()
    
#     return pdf_docs

from langchain_community.document_loaders import PyPDFLoader

def ingest_data(pdf_path):
    # 1. Process PDF
    pdf_loader = PyPDFLoader(pdf_path)
    pdf_docs = pdf_loader.load()
    
    return pdf_docs