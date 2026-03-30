"""
SplitMind Provider Plugin System

Automatic provider discovery and registration system.

Supports:
1. Automatic discovery of built-in providers
2. External provider registration via register_provider()
3. Entry points for pip-installable plugins
"""

from pkgutil import iter_modules
from pathlib import Path
import importlib
import importlib.metadata
from typing import Type

from splitmind.providers.base import BaseProvider
from splitmind.providers.registry import registry

# Expose registry and base classes
export = [
    "BaseProvider",
    "registry",
    "register_provider",
    "ProviderInfo",
    "ProviderCapability",
    "ProviderStatus"
]

# Also import from base to make them available at splitmind.providers
from splitmind.providers.base import (
    ProviderInfo,
    ProviderCapability,
    ProviderStatus
)

# 1. Auto-discover built-in providers
_providers_dir = Path(__file__).parent

# Discover built_in providers
_built_in_dir = _providers_dir / "built_in"
if _built_in_dir.exists():
    for _, name, _ in iter_modules([str(_built_in_dir)]):
        try:
            module = importlib.import_module(f"splitmind.providers.built_in.{name}")
        except Exception as e:
            # Skip modules that fail to import
            pass

# 2. Discover entry point plugins
try:
    # Look for entry points in the 'splitmind.provider' group
    for entry_point in importlib.metadata.entry_points().get('splitmind.provider', []):
        try:
            provider_class = entry_point.load()
            if issubclass(provider_class, BaseProvider):
                # Register the provider class
                registry.register_class(entry_point.name, provider_class)
        except Exception as e:
            # Skip entry points that fail to load
            pass
except Exception:
    # Entry points might not be available in all environments
    pass

# 3. Public API for external registration
def register_provider(provider_class: Type[BaseProvider]) -> None:
    """
    Register a custom provider class.
    
    Args:
        provider_class: A subclass of BaseProvider
    """
    if not issubclass(provider_class, BaseProvider):
        raise ValueError("Provider class must inherit from BaseProvider")
    
    # Use the class name as the provider name
    registry.register_class(provider_class.__name__, provider_class)

# 4. Initialize built-in providers if available
try:
    # Import and initialize common providers if API keys are available
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from splitmind.providers.built_in.openai_provider import OpenAIProvider
        registry.create_provider("openai", api_key=openai_key)
    
    # Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        from splitmind.providers.built_in.anthropic_provider import AnthropicProvider
        registry.create_provider("anthropic", api_key=anthropic_key)
    
    # Kimi
    kimi_key = os.getenv("KIMI_API_KEY")
    if kimi_key:
        from splitmind.providers.built_in.kimi_provider import KimiProvider
        registry.create_provider("kimi", api_key=kimi_key)
    
    # Local (Ollama)
    from splitmind.providers.built_in.local_provider import LocalProvider
    registry.create_provider("local")
    
except Exception:
    # Skip initialization if dependencies are missing
    pass
