"""
Comprehensive test for SplitMind core functionality.

Tests:
1. Multi-provider task distribution
2. Different task splitting strategies
3. Privacy protection in various scenarios
"""

import asyncio
from splitmind_core.privacy import PrivacyHandler
from splitmind_core.splitter import TaskSplitter
from splitmind_core.aggregator import ResultAggregator
from splitmind_providers import ProviderRegistry, LocalProvider, OpenAIProvider, AnthropicProvider, KimiProvider

def test_privacy_protection():
    """Test privacy protection in various scenarios."""
    print("Testing Privacy Protection...")
    print("=" * 60)
    
    handler = PrivacyHandler()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Chinese personal info",
            "text": """
客户信息：
姓名：张三
电话：13812345678
身份证号：320123199001011234
邮箱：zhangsan@example.com
银行账号：6222 0222 0000 1234 567
地址：北京市朝阳区xxx街道123号
            """.strip(),
            "expected_types": ["phone", "email", "id_card_cn", "bank_card"]
        },
        {
            "name": "English personal info",
            "text": """
Personal info:
Name: John Doe
Phone: +1 555-123-4567
Email: john@example.com
Credit card: 4111 1111 1111 1111
SSN: 123-45-6789
            """.strip(),
            "expected_types": ["phone", "email", "credit_card"]
        },
        {
            "name": "Mixed content",
            "text": """
Project report:
Contact: Alice Wang (alice@company.com)
Phone: 13987654321
Budget: ¥1,000,000
IP: 192.168.1.1
URL: https://example.com
            """.strip(),
            "expected_types": ["email", "phone", "amount", "ipv4", "url"]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print("-" * 40)
        
        # Test privacy report
        report = handler.generate_report(scenario['text'])
        print(f"  Risk Level: {report.risk_level}")
        print(f"  Total Items: {report.total_items_detected}")
        print(f"  Detected Types: {list(report.items_by_type.keys())}")
        
        # Test redaction
        redacted, mapping = handler.redact(scenario['text'])
        print(f"  Redaction placeholders: {len(mapping)}")
        print(f"  First 100 chars: {redacted[:100]}...")
        
        # Test restoration
        restored = handler.restore(redacted, mapping)
        print(f"  Restoration successful: {restored == scenario['text']}")
    
    print("\n" + "=" * 60)
    print("Privacy protection test completed!")

def test_task_splitting():
    """Test different task splitting strategies."""
    print("\nTesting Task Splitting Strategies...")
    print("=" * 60)
    
    splitter = TaskSplitter()
    
    # Test tasks
    test_tasks = [
        {
            "name": "Analysis task",
            "text": """
请分析2024年的销售数据：
1. 第一季度销售额
2. 第二季度销售额
3. 第三季度销售额
4. 第四季度销售额
并提供年度趋势分析。
            """.strip(),
            "strategies": ["auto", "section", "parallel"]
        },
        {
            "name": "Creative task",
            "text": """
请创作一个科幻故事，包含以下元素：
1. 未来世界
2. 人工智能
3. 时间旅行
4. 人类情感
            """.strip(),
            "strategies": ["auto", "single", "semantic"]
        }
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task['name']}")
        print("-" * 40)
        
        for strategy in task['strategies']:
            try:
                result = splitter.split(task['text'], strategy=strategy)
                print(f"  Strategy: {strategy}")
                print(f"    Task type: {result.task_type.value}")
                print(f"    Subtasks: {len(result.subtasks)}")
                for i, subtask in enumerate(result.subtasks[:2]):
                    print(f"    Subtask {i+1}: {subtask.task_type.value} - {subtask.description[:50]}...")
            except Exception as e:
                print(f"  Strategy {strategy}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("Task splitting test completed!")

def test_multi_provider_distribution():
    """Test multi-provider task distribution."""
    print("\nTesting Multi-Provider Task Distribution...")
    print("=" * 60)
    
    registry = ProviderRegistry()
    
    # Register providers (with dummy API keys)
    providers = [
        ("local", LocalProvider()),
        ("openai", OpenAIProvider(api_key="test-key")),
        ("anthropic", AnthropicProvider(api_key="test-key")),
        ("kimi", KimiProvider(api_key="test-key")),
    ]
    
    for name, provider in providers:
        try:
            registry.register_provider(name, provider)
            print(f"[OK] {name} provider registered")
        except Exception as e:
            print(f"[X] {name} provider failed: {e}")
    
    # Test provider selection
    print(f"\nTotal providers: {len(registry)}")
    print(f"Provider names: {registry.list_providers()}")
    
    # Test provider status
    status = registry.get_provider_status()
    print("\nProvider status:")
    for name, info in status.items():
        print(f"  {name}: {'Available' if info.get('is_available', False) else 'Unavailable'}")
    
    # Test best provider selection
    test_cases = [
        {"task": "analysis", "capabilities": ["chat"]},
        {"task": "generation", "capabilities": ["chat"]},
        {"task": "vision", "capabilities": ["vision"]},
    ]
    
    print("\nBest provider selection:")
    for test_case in test_cases:
        best = registry.get_best_provider(
            task_type=test_case["task"],
            required_capabilities=test_case["capabilities"]
        )
        if best:
            print(f"  Task: {test_case['task']} - Best provider: {best}")
        else:
            print(f"  Task: {test_case['task']} - No suitable provider")
    
    print("\n" + "=" * 60)
    print("Multi-provider distribution test completed!")

def test_full_pipeline():
    """Test full pipeline: privacy protection + task splitting + aggregation."""
    print("\nTesting Full Pipeline...")
    print("=" * 60)
    
    handler = PrivacyHandler()
    splitter = TaskSplitter()
    aggregator = ResultAggregator()
    
    # Test task with sensitive information
    sensitive_task = """
请分析客户数据：
1. 客户：李明（电话13912345678）
2. 订单号：ORD2024001
3. 金额：5000元
4. 邮箱：liming@example.com
5. 地址：上海市浦东新区xxx路123号
    """.strip()
    
    print("Step 1: Original task")
    print(f"First 100 chars: {sensitive_task[:100]}...")
    
    print("\nStep 2: Privacy protection")
    redacted, mapping = handler.redact(sensitive_task)
    print(f"Redacted: {redacted[:100]}...")
    
    print("\nStep 3: Task splitting")
    split_result = splitter.split(redacted, strategy="section")
    print(f"Split into {len(split_result.subtasks)} subtasks")
    
    print("\nStep 4: Simulate processing")
    simulated_results = []
    for i, subtask in enumerate(split_result.subtasks):
        from splitmind_core.aggregator import SubTaskResult
        simulated_results.append(SubTaskResult(
            subtask_id=subtask.id,
            provider=f"provider_{i+1}",
            result=f"Processed subtask: {subtask.description[:30]}... (simulated result)"
        ))
    
    print("\nStep 5: Result aggregation")
    aggregated = aggregator.aggregate(simulated_results, strategy="sequential")
    print(f"Aggregated result: {aggregated.final_result}")
    
    print("\nStep 6: Restore sensitive info")
    final_with_pii = handler.restore(aggregated.final_result, mapping)
    print(f"Final result: {final_with_pii[:100]}...")
    
    print("\n" + "=" * 60)
    print("Full pipeline test completed!")

def main():
    """Main test function."""
    print("SplitMind Comprehensive Core Functionality Test")
    print("=" * 60)
    
    test_privacy_protection()
    test_task_splitting()
    test_multi_provider_distribution()
    test_full_pipeline()
    
    print("\n" + "=" * 60)
    print("All comprehensive tests completed!")

if __name__ == "__main__":
    main()
