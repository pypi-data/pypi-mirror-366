"""
LangChain Zunno Integration

A LangChain integration for Zunno LLM and Embeddings.
"""

from .llm import ZunnoLLM, create_zunno_llm
from .embeddings import ZunnoLLMEmbeddings, create_zunno_embeddings

__version__ = "0.1.0"
__author__ = "Amit Kumar"
__email__ = "amit@zunno.ai"

__all__ = [
    "ZunnoLLM",
    "ZunnoLLMEmbeddings", 
    "create_zunno_llm",
    "create_zunno_embeddings",
] 