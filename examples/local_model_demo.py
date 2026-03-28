"""
Local Model Demo - Demonstrate privacy-preserving AI with local models.

This example shows how to use SplitMind with local Ollama models,
keeping all data on your machine for maximum privacy.
"""

import asyncio
from splitmind.providers.local_provider_v2 import LocalProviderV2
from splitmind.providers.ollama_manager import LocalModelSetup, OllamaManager


async def check_setup():
    """Check if Ollama is installed and running."""
    print("=" * 60)
    print("SplitMind Local Model Setup Check")
    print("=" * 60)
    
    # Check if Ollama is installed
    if LocalModelSetup.check_ollama_installed():
        print("[OK] Ollama is installed")
    else:
        print("[X] Ollama is not installed")
        print(LocalModelSetup.get_install_instructions())
        return False
    
    # Check if Ollama is running
    manager = OllamaManager()
    if await manager.is_running():
        print("[OK] Ollama server is running")
    else:
        print("[X] Ollama server is not running")
        print("Please start Ollama:")
        print("  - Windows: Start Ollama from Start menu")
        print("  - macOS/Linux: Run 'ollama serve'")
        return False
    
    # List available models
    models = await manager.list_models()
    if models:
        print(f"\nInstalled models ({len(models)}):")
        for model in models:
            print(f"  - {model['name']}")
    else:
        print("\nNo models installed yet")
    
    await manager.close()
    return True


async def demo_privacy_with_local_model():
    """Demo: Process sensitive data with local model."""
    print("\n" + "=" * 60)
    print("Privacy-Preserving Local AI Demo")
    print("=" * 60)
    
    # Sensitive data that should never leave your machine
    sensitive_text = """
客户投诉记录：
客户姓名：李明
联系电话：13912345678
身份证号：31010119900307888X
投诉内容：我购买的商品（订单号：ORD20240328001）
在2024年3月15日送达时发现损坏，
要求退款至银行卡：6222 0222 0000 1234 567
联系邮箱：liming@example.com
    """.strip()
    
    print("\nOriginal text (contains PII):")
    print(sensitive_text)
    print("\n" + "-" * 60)
    
    # Step 1: Create provider (auto-downloads model if needed)
    print("\nStep 1: Initializing local model provider...")
    provider = LocalProviderV2(auto_setup=True)
    
    # Step 2: Process with privacy protection
    print("\nStep 2: Processing with local AI (data never leaves your machine)...")
    
    prompt = f"""
Please analyze this customer complaint and extract key information:
1. Customer name
2. Contact info
3. Order number
4. Issue description
5. Requested resolution

Text:
{sensitive_text}

Provide a structured summary.
"""
    
    try:
        result = await provider.generate_async(
            prompt=prompt,
            task_type="analysis"
        )
        
        print("\nAI Analysis Result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Ollama is running and a model is available.")
        return
    
    print("\n" + "-" * 60)
    print("[OK] All processing done locally - no data sent to cloud!")
    print("=" * 60)


async def demo_model_management():
    """Demo: Manage local models."""
    print("\n" + "=" * 60)
    print("Local Model Management Demo")
    print("=" * 60)
    
    manager = OllamaManager()
    
    if not await manager.is_running():
        print("Ollama is not running. Please start it first.")
        return
    
    # Show recommended models (2025 updated)
    print("\nRecommended models for different tasks:")
    for task, info in manager.RECOMMENDED_MODELS.items():
        print(f"  {task}: {info['name']} - {info['description']} ({info['size']})")
    
    # Check system info
    print("\nChecking system...")
    sys_info = await manager.get_system_info()
    print(f"  Available memory: {sys_info['available_memory_gb']:.1f} GB")
    print(f"  Recommended models: {sys_info['recommended']}")
    
    await manager.close()


async def main():
    """Main demo function."""
    print("SplitMind Local Model Demo")
    print("Privacy-preserving AI processing with local models\n")
    
    # First check setup
    if not await check_setup():
        print("\nPlease complete the setup and try again.")
        return
    
    # Show model management options
    await demo_model_management()
    
    # Run privacy demo
    await demo_privacy_with_local_model()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install Ollama if not already installed")
    print("2. Start Ollama server")
    print("3. Run this demo again to see local AI in action")
    print("4. Use SplitMind with LocalProviderV2 for privacy")


if __name__ == "__main__":
    asyncio.run(main())
