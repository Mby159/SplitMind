"""
Provider Registry - Manages AI providers and their capabilities.
"""

from typing import Dict, List, Optional, Type
from splitmind_providers.base import BaseProvider


class ProviderRegistry:
    """
    Registry for AI providers.
    
    This class manages a collection of AI providers and provides methods
    to register, retrieve, and query provider capabilities.
    """
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._provider_classes: Dict[str, Type[BaseProvider]] = {}
    
    def register_provider(self, name: str, provider: BaseProvider) -> None:
        """
        Register a provider instance.
        
        Args:
            name: Provider name
            provider: Provider instance
        """
        self._providers[name] = provider
    
    def register_provider_class(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider class.
        
        Args:
            name: Provider name
            provider_class: Provider class
        """
        self._provider_classes[name] = provider_class
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """
        Get a provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(name)
    
    def get_provider_class(self, name: str) -> Optional[Type[BaseProvider]]:
        """
        Get a provider class by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider class or None if not found
        """
        return self._provider_classes.get(name)
    
    def list_providers(self) -> List[str]:
        """
        List all registered providers.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def list_provider_classes(self) -> List[str]:
        """
        List all registered provider classes.
        
        Returns:
            List of provider class names
        """
        return list(self._provider_classes.keys())
    
    def get_provider_status(self) -> Dict[str, Dict]:
        """
        Get status of all providers.
        
        Returns:
            Dict with provider names as keys and status info as values
        """
        status = {}
        for name, provider in self._providers.items():
            try:
                info = provider.get_info()
                status[name] = {
                    "model": provider.model,
                    "max_tokens": info.max_tokens,
                    "capabilities": [cap.value for cap in info.capabilities],
                    "is_available": provider.validate_connection(),
                }
            except Exception as e:
                status[name] = {
                    "model": provider.model,
                    "error": str(e),
                    "is_available": False,
                }
        return status
    
    def get_providers_by_capability(self, capability: str) -> List[BaseProvider]:
        """
        Get providers that support a specific capability.
        
        Args:
            capability: Capability name
            
        Returns:
            List of provider instances
        """
        providers = []
        for provider in self._providers.values():
            try:
                info = provider.get_info()
                if any(cap.value == capability for cap in info.capabilities):
                    providers.append(provider)
            except Exception:
                pass
        return providers
    
    def get_best_provider(self, task_type: str, required_capabilities: List[str] = None) -> Optional[BaseProvider]:
        """
        Get the best provider for a specific task.
        
        Args:
            task_type: Task type
            required_capabilities: Required capabilities
            
        Returns:
            Best provider instance or None if no suitable provider found
        """
        suitable_providers = []
        
        for provider in self._providers.values():
            try:
                info = provider.get_info()
                
                # Check capabilities
                if required_capabilities:
                    has_capabilities = all(
                        any(cap.value == req for cap in info.capabilities)
                        for req in required_capabilities
                    )
                    if not has_capabilities:
                        continue
                
                suitable_providers.append(provider)
            except Exception:
                pass
        
        if not suitable_providers:
            return None
        
        # Simple selection: return the first one
        return suitable_providers[0]
    
    def clear(self):
        """
        Clear all registered providers.
        """
        self._providers.clear()
    
    def __contains__(self, name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            name: Provider name
            
        Returns:
            True if provider is registered
        """
        return name in self._providers
    
    def __len__(self) -> int:
        """
        Get the number of registered providers.
        
        Returns:
            Number of providers
        """
        return len(self._providers)
