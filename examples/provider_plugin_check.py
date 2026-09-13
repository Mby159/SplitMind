#!/usr/bin/env python3
"""
Check script for the SplitMind provider plugin system.

运行：python examples/provider_plugin_check.py（在仓库根目录执行）
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path (independent of the caller's cwd)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows 控制台默认 GBK，而本脚本会打印 ✓/✅，否则直接 UnicodeEncodeError 中断
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
        print(f"  ✓ {provider_name}: available (model: {info.models[0] if info.models else 'N/A'})")
    else:
        print(f"  ⚠ {provider_name}: not initialized (API key not found?)")
print()

# Test 3: Test external provider registration
print("3. Testing external provider registration...")

class TestProvider(BaseProvider):
    """Test provider for plugin system"""
    
    def _default_model(self) -> str:
        return "test-model"
    
    def get_info(self):
        return ProviderInfo(
            name="test",
            description="Test provider",
            models=[self.model],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096,
            supports_streaming=False
        )
    
    def generate(self, prompt, **kwargs):
        return f"Test response: {prompt}"
    
    async def generate_async(self, prompt, **kwargs):
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
    info = local_provider.get_info()
    print(f"  ✓ Created local provider: {info.models[0] if info.models else 'N/A'}")
else:
    print("  ⚠ Could not create local provider")

# Test 5: Test listing all providers
print("\n5. Testing provider listing...")
print(f"All providers: {registry.list_providers()}")
print(f"All provider classes: {list(registry._provider_classes.keys())}")

print("\n✅ Provider plugin system test completed!")
