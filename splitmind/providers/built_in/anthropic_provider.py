"""
Anthropic Provider - Implementation for Claude models.
"""

from typing import Optional
import asyncio

from splitmind.providers.base import BaseProvider, ProviderInfo, ProviderCapability


class AnthropicProvider(BaseProvider):
    """
    Anthropic Provider - Supports Claude 3 and newer models.
    """
    
    def _default_model(self) -> str:
        return "claude-3-opus-20240229"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anthropic",
            description="Anthropic Claude models including Claude 3 Opus, Sonnet, and Haiku",
            models=[
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
            ],
            capabilities=[
                ProviderCapability.CHAT,
                ProviderCapability.VISION,
            ],
            max_tokens=200000,
            supports_streaming=True,
        )
    
    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
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
        
        response = client.messages.create(
            model=self.model,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            system=system,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        
        return response.content[0].text
    
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
        
        response = await asyncio.to_thread(
            client.messages.create,
            model=self.model,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            system=system,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        
        return response.content[0].text
    
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
        
        with client.messages.stream(
            model=self.model,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            system=system,
            messages=[
                {"role": "user", "content": prompt},
            ],
        ) as stream:
            for text in stream.text_stream:
                yield text
