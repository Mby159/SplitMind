"""
Kimi Provider - Implementation for Moonshot AI's Kimi models.
"""

from typing import Optional
import asyncio
import httpx

from splitmind.providers.base import BaseProvider, ProviderInfo, ProviderCapability


class KimiProvider(BaseProvider):
    """
    Kimi Provider - Supports Moonshot AI's Kimi models.
    
    Kimi is a Chinese AI model by Moonshot AI with strong
    long-context capabilities.
    """
    
    def _default_model(self) -> str:
        return "moonshot-v1-8k"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="kimi",
            description="Moonshot AI Kimi models with long context support",
            models=[
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
            ],
            max_tokens=128000 if "128k" in self.model else (32000 if "32k" in self.model else 8000),
            supports_streaming=True,
        )
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                base_url = self.base_url or "https://api.moonshot.cn/v1"
                self._client = OpenAI(
                    api_key=self.api_key,
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
