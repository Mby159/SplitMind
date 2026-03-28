"""
Provider Registry - Manages multiple AI providers.
"""

from typing import Dict, List, Optional, Type
from splitmind.providers.base import BaseProvider, ProviderInfo


class ProviderRegistry:
    """
    Registry for managing multiple AI providers.
    
    Supports:
    - Registering/unregistering providers
    - Listing available providers
    - Getting provider by name
    - Provider discovery and selection
    """
    
    _instance = None
    _providers: Dict[str, BaseProvider] = {}
    _provider_classes: Dict[str, Type[BaseProvider]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, provider: BaseProvider) -> None:
        info = provider.get_info()
        self._providers[info.name] = provider
    
    def unregister(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseProvider]:
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        return list(self._providers.keys())
    
    def get_all_info(self) -> Dict[str, ProviderInfo]:
        return {
            name: provider.get_info()
            for name, provider in self._providers.items()
        }
    
    def register_class(self, name: str, provider_class: Type[BaseProvider]) -> None:
        self._provider_classes[name] = provider_class
    
    def create_provider(
        self,
        name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> Optional[BaseProvider]:
        provider_class = self._provider_classes.get(name)
        if not provider_class:
            return None
        
        provider = provider_class(
            api_key=api_key,
            base_url=base_url,
            model=model,
            **kwargs,
        )
        self.register(provider)
        return provider
    
    def select_best_provider(
        self,
        task_type: Optional[str] = None,
        require_capability: Optional[str] = None,
    ) -> Optional[BaseProvider]:
        if not self._providers:
            return None
        
        if len(self._providers) == 1:
            return list(self._providers.values())[0]
        
        scores = {}
        for name, provider in self._providers.items():
            score = 0
            info = provider.get_info()
            
            score += len(info.capabilities) * 10
            
            if task_type:
                task_capability_map = {
                    "analysis": "chat",
                    "generation": "chat",
                    "summarization": "chat",
                    "translation": "chat",
                    "extraction": "chat",
                    "classification": "chat",
                    "reasoning": "chat",
                }
                required_cap = task_capability_map.get(task_type, "chat")
                if required_cap in [c.value for c in info.capabilities]:
                    score += 50
            
            if require_capability:
                if require_capability in [c.value for c in info.capabilities]:
                    score += 100
                else:
                    score -= 1000
            
            score += info.max_tokens // 1000
            
            scores[name] = score
        
        best_name = max(scores, key=scores.get)
        return self._providers[best_name]
    
    def get_provider_status(self) -> Dict[str, Dict]:
        status = {}
        for name, provider in self._providers.items():
            info = provider.get_info()
            status[name] = {
                "model": provider.model,
                "capabilities": [c.value for c in info.capabilities],
                "max_tokens": info.max_tokens,
                "supports_streaming": info.supports_streaming,
            }
        return status
    
    def clear(self) -> None:
        self._providers.clear()


registry = ProviderRegistry()
