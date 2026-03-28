"""
OpenAI Provider - Implementation for OpenAI API.
"""

import asyncio
from typing import Optional

from splitmind_providers.base import BaseProvider, ProviderInfo, ProviderCapability


class OpenAIProvider(BaseProvider):
    """
    OpenAI Provider - Supports OpenAI's API.
    
    Compatible with:
    - OpenAI GPT-4o
    - OpenAI GPT-4
    - OpenAI GPT-3.5 Turbo
    - Azure OpenAI
    """
    
    def _default_model(self) -> str:
        return "gpt-3.5-turbo"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openai",
            description="OpenAI API provider",
            models=[
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
                ProviderCapability.VISION,
                ProviderCapability.FUNCTION_CALLING,
            ],
            max_tokens=16384,
            supports_streaming=True,
        )
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
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
            frequency_penalty=config["frequency_penalty"],
            presence_penalty=config["presence_penalty"],
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
            frequency_penalty=config["frequency_penalty"],
            presence_penalty=config["presence_penalty"],
        )
        
        return response.choices[0].message.content or ""
