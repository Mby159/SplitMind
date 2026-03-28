"""
Local Provider V2 - Enhanced local model support with auto-setup.
"""

import asyncio
from typing import Optional, AsyncGenerator

from splitmind.providers.base import BaseProvider, ProviderInfo, ProviderCapability
from splitmind.providers.ollama_manager import OllamaManager, LocalModelSetup


class LocalProviderV2(BaseProvider):
    """
    Enhanced Local Provider with automatic model management.
    
    Features:
    - Auto-detect Ollama installation
    - Auto-download recommended models
    - Smart model selection based on task type
    - Fallback to smaller models if needed
    - Zero configuration for first-time users
    
    Usage:
        provider = LocalProviderV2()
        # Auto-setup on first use
        result = await provider.generate_async("Hello!")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[dict] = None,
        auto_setup: bool = True,
    ):
        super().__init__(api_key, base_url, model, config)
        self.manager = OllamaManager(host=base_url)
        self._setup_complete = False
        self._auto_setup = auto_setup
    
    def _default_model(self) -> str:
        return "llama3.2:3b"
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="local_v2",
            description="Enhanced local provider with auto-setup (Ollama, 2025 updated)",
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
    
    async def _ensure_setup(self) -> bool:
        """Ensure Ollama is set up and a model is available."""
        if self._setup_complete:
            return True
        
        if not self._auto_setup:
            return await self.manager.is_running()
        
        # Check if Ollama is installed
        if not LocalModelSetup.check_ollama_installed():
            print(LocalModelSetup.get_install_instructions())
            return False
        
        # Check if Ollama is running
        if not await self.manager.is_running():
            print("""
Ollama is installed but not running.
Please start Ollama first:
    - Windows: Start Ollama from the Start menu or system tray
    - macOS/Linux: Run 'ollama serve' in terminal
            """)
            return False
        
        # Ensure the model is available
        if not await self.manager.ensure_model(self.model):
            # Try fallback models (2025 updated)
            fallbacks = ["llama3.2:3b", "gemma3:1b", "llama3.2:1b", "qwen2.5:3b"]
            for fallback in fallbacks:
                if fallback != self.model:
                    print(f"Trying fallback model: {fallback}")
                    if await self.manager.ensure_model(fallback):
                        self.model = fallback
                        break
            else:
                print("Failed to download any model. Please check your internet connection.")
                return False
        
        self._setup_complete = True
        return True
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate text (sync version)."""
        return asyncio.run(self.generate_async(prompt, system_prompt, task_type, **kwargs))
    
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate text (async version)."""
        if not await self._ensure_setup():
            return "Error: Local model not available. Please install and start Ollama."
        
        system = system_prompt or self._build_system_prompt(task_type)
        
        # Use Ollama native API for better control
        return await self.manager.chat(
            model=self.model,
            message=prompt,
            system=system,
        )
    
    async def generate_stream_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming (async generator)."""
        if not await self._ensure_setup():
            yield "Error: Local model not available."
            return
        
        system = system_prompt or self._build_system_prompt(task_type)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        import httpx
        import json
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.manager.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
    
    def validate_connection(self) -> bool:
        """Check if the local model is accessible."""
        return asyncio.run(self._validate_connection_async())
    
    async def _validate_connection_async(self) -> bool:
        """Async version of validate_connection."""
        if not LocalModelSetup.check_ollama_installed():
            return False
        
        if not await self.manager.is_running():
            return False
        
        # Try a simple test message
        try:
            result = await self.manager.chat(self.model, "Hi", None)
            return len(result) > 0
        except Exception:
            return False
    
    async def list_available_models(self) -> list:
        """List all locally available models."""
        if not await self.manager.is_running():
            return []
        return await self.manager.list_models()
    
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        if await self.manager.ensure_model(model_name):
            self.model = model_name
            return True
        return False
    
    def get_status(self) -> dict:
        """Get current provider status."""
        return {
            "type": "local_v2",
            "model": self.model,
            "setup_complete": self._setup_complete,
            "auto_setup": self._auto_setup,
            "host": self.manager.host,
        }
