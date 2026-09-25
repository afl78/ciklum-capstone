"""
Exposing the core functions here allows for cleaner imports in main.py.
"""

from .ingestion import ingest_data
from .vector_store import create_vector_db, load_existing_db
from .generator import query_chatbot
from .agent import create_rag_agent
from .tools import get_tools
from .evaluator import evaluate_performance

# Define __all__ to control what is exported when someone uses 'from modules import *'
__all__ = [
    "ingest_data",
    "create_vector_db",
    "load_existing_db",
    "query_chatbot",
    "get_tools",
    "create_rag_agent",
    "evaluate_performance"
]