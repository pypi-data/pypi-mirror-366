"""
LangChain LLM integration for Zunno.
"""

from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests


class ZunnoLLM(LLM):
    """Zunno LLM wrapper for LangChain."""
    
    model_name: str
    base_url: str = "http://15.206.124.44/v1/prompt-response"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 300
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "zunno"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "base_url": self.base_url,
        }
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Zunno API."""
        try:
            payload = {
                "model_name": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                }
            }
            
            if self.max_tokens:
                payload["options"]["num_predict"] = self.max_tokens
            
            if stop:
                payload["options"]["stop"] = stop
            
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Zunno API error: {response.text}")
            
            data = response.json()
            return data.get("response", "")
            
        except Exception as e:
            raise Exception(f"Error calling Zunno LLM: {e}")
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Async call to the Zunno API."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model_name": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                    }
                }
                
                if self.max_tokens:
                    payload["options"]["num_predict"] = self.max_tokens
                
                if stop:
                    payload["options"]["stop"] = stop
                
                response = await client.post(
                    self.base_url,
                    json=payload
                )

                if response.status_code != 200:
                    raise Exception(f"Zunno API error: {response.text}")
                
                data = response.json()
                return data.get("response", "")
                
        except Exception as e:
            raise Exception(f"Error calling Zunno LLM: {e}")


def create_zunno_llm(
    model_name: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    base_url: str = "http://15.206.124.44/v1/prompt-response",
    timeout: int = 300
) -> ZunnoLLM:
    """Create a Zunno LLM instance."""
    return ZunnoLLM(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
        timeout=timeout
    ) 