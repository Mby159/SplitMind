"""
Anthropic Provider - Implementation for Anthropic API (Claude).
"""

import asyncio
from typing import Optional

from splitmind_providers.base import BaseProvider, ProviderInfo, ProviderCapability


class AnthropicProvider(BaseProvider):
    """
    Anthropic Provider - Supports Anthropic's Claude models.
    
    Compatible with:
    - Claude 3 Opus
    - Claude 3 Sonnet
    - Claude 3 Haiku
    - Claude 2
    """
    
    def _default_model(self) -> str:
        return "claude-3-sonnet-20240229"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anthropic",
            description="Anthropic API provider (Claude)",
            models=[
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240229",
                "claude-2.1",
                "claude-2.0",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.COMPLETION,
                ProviderCapability.VISION,
                ProviderCapability.FUNCTION_CALLING,
            ],
            max_tokens=200000,
            supports_streaming=True,
        )
    
    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. "
                    "Please install it with: pip install anthropic"
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
        
        message = client.messages.create(
            model=self.model,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
        )
        
        return message.content[0].text if message.content else ""
    
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
        
        message = await asyncio.to_thread(
            client.messages.create,
            model=self.model,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
        )
        
        return message.content[0].text if message.content else ""
