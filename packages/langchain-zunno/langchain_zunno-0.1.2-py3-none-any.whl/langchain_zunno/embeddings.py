"""
LangChain Embeddings integration for Zunno.
"""

from typing import List
from langchain.embeddings.base import Embeddings
import requests


class ZunnoLLMEmbeddings(Embeddings):
    """Zunno Embeddings wrapper for LangChain."""
    
    model_name: str
    base_url: str = "http://15.206.124.44/v1/text-embeddings"
    timeout: int = 300
    
    def __init__(self, model_name: str, base_url: str = None, timeout: int = 300):
        super().__init__()
        self.model_name = model_name
        if base_url:
            self.base_url = base_url
        self.timeout = timeout
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        try:
            payload = {
                "model_name": self.model_name,
                "text": text,
                "options": {
                    "normalize": True
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Zunno embeddings API error: {response.text}")
            
            data = response.json()
            embeddings = data.get("embeddings", [])
            
            if not embeddings:
                raise Exception("No embeddings returned from API")
                
            return embeddings
            
        except Exception as e:
            raise Exception(f"Error getting text embeddings: {e}")
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = await self.aembed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async embed a single query."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model_name": self.model_name,
                    "text": text,
                    "options": {
                        "normalize": True
                    }
                }
                
                response = await client.post(
                    self.base_url,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Zunno embeddings API error: {response.text}")
                
                data = response.json()
                embeddings = data.get("embeddings", [])
                
                if not embeddings:
                    raise Exception("No embeddings returned from API")
                    
                return embeddings
                
        except Exception as e:
            raise Exception(f"Error getting text embeddings: {e}")


def create_zunno_embeddings(
    model_name: str,
    base_url: str = "http://15.206.124.44/v1/text-embeddings",
    timeout: int = 300
) -> ZunnoLLMEmbeddings:
    """Create a Zunno Embeddings instance."""
    return ZunnoLLMEmbeddings(
        model_name=model_name,
        base_url=base_url,
        timeout=timeout
    ) 