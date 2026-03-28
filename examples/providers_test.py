"""
Test script for splitmind-providers core functionality.
"""

from splitmind_providers import (
    ProviderRegistry,
    LocalProvider,
    OpenAIProvider,
    AnthropicProvider,
    KimiProvider
)

def test_provider_registry():
    """Test provider registry functionality."""
    print("Testing Provider Registry...")
    print("=" * 60)
    
    # Create registry
    registry = ProviderRegistry()
    print(f"[OK] Registry created")
    
    # Test LocalProvider
    try:
        local_provider = LocalProvider()
        registry.register_provider("local", local_provider)
        print(f"[OK] LocalProvider registered")
    except Exception as e:
        print(f"[X] LocalProvider failed: {e}")
    
    # Test registry methods
    print(f"\nRegistered providers: {registry.list_providers()}")
    print(f"Provider count: {len(registry)}")
    print(f"'local' in registry: {'local' in registry}")
    
    # Test provider info
    if "local" in registry:
        provider = registry.get_provider("local")
        info = provider.get_info()
        print(f"\nLocal provider info:")
        print(f"  Name: {info.name}")
        print(f"  Description: {info.description}")
        print(f"  Models: {info.models[:3]}...")
        print(f"  Capabilities: {[cap.value for cap in info.capabilities]}")
        print(f"  Max tokens: {info.max_tokens}")
    
    # Test provider status
    print("\nTesting provider status...")
    status = registry.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'Available' if info.get('is_available', False) else 'Unavailable'}")
        if 'error' in info:
            print(f"    Error: {info['error']}")
    
    # Test get best provider
    print("\nTesting get best provider...")
    best_provider = registry.get_best_provider(
        task_type="analysis",
        required_capabilities=["chat"]
    )
    if best_provider:
        print(f"  Best provider: {best_provider}")
    else:
        print(f"  No suitable provider found")
    
    print("\n" + "=" * 60)
    print("Registry test completed!")

def test_provider_basic():
    """Test basic provider functionality."""
    print("\nTesting Basic Provider Functionality...")
    print("=" * 60)
    
    # Test LocalProvider basic info
    try:
        local_provider = LocalProvider()
        print(f"[OK] LocalProvider created")
        
        # Test token estimation
        test_text = "Hello, this is a test text in English and Chinese 你好，这是中文测试"
        tokens = local_provider.estimate_tokens(test_text)
        print(f"Token estimation: {tokens} tokens for text: '{test_text}'")
        
        # Test system prompt generation
        system_prompt = local_provider._build_system_prompt("analysis")
        print(f"System prompt for analysis: '{system_prompt}'")
        
    except Exception as e:
        print(f"[X] LocalProvider test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Basic provider test completed!")

def test_provider_classes():
    """Test all provider classes."""
    print("\nTesting Provider Classes...")
    print("=" * 60)
    
    providers = [
        ("LocalProvider", LocalProvider),
        ("OpenAIProvider", OpenAIProvider),
        ("AnthropicProvider", AnthropicProvider),
        ("KimiProvider", KimiProvider),
    ]
    
    for name, provider_class in providers:
        try:
            # Create provider without API key (should not throw)
            provider = provider_class(api_key="test-key")
            info = provider.get_info()
            print(f"[OK] {name} created")
            print(f"  Models: {info.models[:2]}...")
            print(f"  Capabilities: {[cap.value for cap in info.capabilities[:2]]}...")
        except Exception as e:
            print(f"[X] {name} failed: {e}")
    
    print("\n" + "=" * 60)
    print("Provider classes test completed!")

def main():
    """Main test function."""
    print("SplitMind Providers Core Functionality Test")
    print("=" * 60)
    
    test_provider_registry()
    test_provider_basic()
    test_provider_classes()
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()
