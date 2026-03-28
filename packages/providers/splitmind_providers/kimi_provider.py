"""
Kimi Provider - Implementation for Kimi API.
"""

import asyncio
from typing import Optional
import httpx

from splitmind_providers.base import BaseProvider, ProviderInfo, ProviderCapability


class KimiProvider(BaseProvider):
    """
    Kimi Provider - Supports Kimi's API.
    
    Compatible with:
    - Kimi Moonshot
    - Kimi Pro
    - Kimi Max
    """
    
    def _default_model(self) -> str:
        return "kimi"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="kimi",
            description="Kimi API provider",
            models=[
                "kimi",
                "kimi-pro",
                "kimi-max",
                "kimi-coder",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
                ProviderCapability.VISION,
            ],
            max_tokens=128000,
            supports_streaming=True,
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        system = system_prompt or self._build_system_prompt(task_type)
        config = self._merge_config(**kwargs)
        
        base_url = self.base_url or "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "top_p": config["top_p"],
        }
        
        response = httpx.post(base_url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"] or ""
    
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        system = system_prompt or self._build_system_prompt(task_type)
        config = self._merge_config(**kwargs)
        
        base_url = self.base_url or "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "top_p": config["top_p"],
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"] or ""
