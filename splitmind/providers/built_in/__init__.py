"""
Built-in providers for SplitMind
"""

from splitmind.providers.registry import registry

# Import and register all built-in providers
try:
    from splitmind.providers.built_in.openai_provider import OpenAIProvider
    registry.register_class("OpenAIProvider", OpenAIProvider)
    registry.register_class("openai", OpenAIProvider)  # Alias for easy access
except Exception:
    pass

try:
    from splitmind.providers.built_in.anthropic_provider import AnthropicProvider
    registry.register_class("AnthropicProvider", AnthropicProvider)
    registry.register_class("anthropic", AnthropicProvider)  # Alias for easy access
except Exception:
    pass

try:
    from splitmind.providers.built_in.kimi_provider import KimiProvider
    registry.register_class("KimiProvider", KimiProvider)
    registry.register_class("kimi", KimiProvider)  # Alias for easy access
except Exception:
    pass

try:
    from splitmind.providers.built_in.local_provider import LocalProvider
    registry.register_class("LocalProvider", LocalProvider)
    registry.register_class("local", LocalProvider)  # Alias for easy access
except Exception:
    pass
