"""
Local Provider - Implementation for locally deployed models (Ollama, LM Studio, etc.).
"""

import asyncio
from typing import Optional, AsyncGenerator
import httpx

from splitmind_providers.base import BaseProvider, ProviderInfo, ProviderCapability


class LocalProvider(BaseProvider):
    """
    Local Provider - Supports locally deployed models.
    
    Compatible with:
    - Ollama
    - LM Studio
    - LocalAI
    - vLLM
    - Any OpenAI-compatible local server
    """
    
    def _default_model(self) -> str:
        return "llama3.2:3b"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="local",
            description="Locally deployed models via OpenAI-compatible API",
            models=[
                "llama3.2:3b",
                "llama3.2:1b",
                "gemma3:1b",
                "qwen2.5:3b",
                "qwen2.5-coder:1.5b",
                "olmo2:7b",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
            ],
            max_tokens=32768,
            supports_streaming=True,
        )
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                base_url = self.base_url or "http://localhost:11434/v1"
                self._client = OpenAI(
                    api_key=self.api_key or "ollama",
                    base_url=base_url,
                )
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Please install it with: pip install openai"
                )
        return self._client
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        client = self._get_client()
        
        system = system_prompt or self._build_system_prompt(task_type)
        config = self._merge_config(**kwargs)
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
        )
        
        return response.choices[0].message.content or ""
    
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        client = self._get_client()
        
        system = system_prompt or self._build_system_prompt(task_type)
        config = self._merge_config(**kwargs)
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
        )
        
        return response.choices[0].message.content or ""
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ):
        client = self._get_client()
        
        system = system_prompt or self._build_system_prompt(task_type)
        config = self._merge_config(**kwargs)
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        stream = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def check_server_health(self) -> bool:
        base_url = self.base_url or "http://localhost:11434"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def list_local_models(self) -> list:
        base_url = self.base_url or "http://localhost:11434"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/api/tags", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        
        return []
