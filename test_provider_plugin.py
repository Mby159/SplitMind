#!/usr/bin/env python3
"""
Test script for SplitMind provider plugin system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from splitmind.providers import (
    registry, 
    register_provider,
    BaseProvider,
    ProviderInfo,
    ProviderCapability,
    ProviderStatus
)

print("Testing SplitMind Provider Plugin System...\n")

# Test 1: Check if registry is available
print("1. Testing registry initialization...")
print(f"Registry instance: {registry}")
print(f"Registered providers: {registry.list_providers()}")
print(f"Provider classes: {list(registry._provider_classes.keys())}")
print("✓ Registry initialized successfully\n")

# Test 2: Try to get built-in providers
print("2. Testing built-in providers...")
for provider_name in ['openai', 'anthropic', 'kimi', 'local']:
    provider = registry.get(provider_name)
    if provider:
        info = provider.get_info()
        print(f"  ✓ {provider_name}: available (model: {info.model})")
    else:
        print(f"  ⚠ {provider_name}: not initialized (API key not found?)")
print()

# Test 3: Test external provider registration
print("3. Testing external provider registration...")

class TestProvider(BaseProvider):
    """Test provider for plugin system"""
    
    def __init__(self, api_key=None, base_url=None, model="test-model", **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, model=model, **kwargs)
    
    def get_info(self):
        return ProviderInfo(
            name="test",
            model=self.model,
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096,
            supports_streaming=False
        )
    
    async def generate(self, prompt, **kwargs):
        return f"Test response: {prompt}"

# Register the test provider
register_provider(TestProvider)

# Create an instance
print(f"  Registering TestProvider...")
test_provider = registry.create_provider("TestProvider", model="test-1.0")

if test_provider:
    print(f"  ✓ TestProvider registered successfully")
    info = test_provider.get_info()
    print(f"  Provider info: {info}")
    print("✓ External provider registration works\n")
else:
    print("  ✗ Failed to register TestProvider")

# Test 4: Test provider creation by name
print("4. Testing provider creation by name...")
local_provider = registry.create_provider("local", model="llama3.2:3b")
if local_provider:
    print(f"  ✓ Created local provider: {local_provider.get_info().model}")
else:
    print("  ⚠ Could not create local provider")

# Test 5: Test listing all providers
print("\n5. Testing provider listing...")
print(f"All providers: {registry.list_providers()}")
print(f"All provider classes: {list(registry._provider_classes.keys())}")

print("\n✅ Provider plugin system test completed!")
