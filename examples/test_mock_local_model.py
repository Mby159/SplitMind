#!/usr/bin/env python3
"""
Test script for Core module with mock local model.
"""

from splitmind.core.engine import SplitMindEngine, ExecutionConfig
from splitmind.core.local_model import LocalModelConfig, LocalModelBackend
from mock_local_model import MockLocalModelInterface


def main():
    print("=== SplitMind Core Test with Mock Local Model ===")
    print("Testing Core module with simulated local model")
    print()
    
    # Create mock local model
    local_model_config = LocalModelConfig(
        model_name="mock-model",
        backend=LocalModelBackend.OLLAMA,
        base_url="http://localhost:11434/api",
        timeout=30,
        max_retries=3,
        temperature=0.7,
        max_tokens=512
    )
    
    # Create SplitMind Engine with mock local model
    engine = SplitMindEngine(
        local_model_config=local_model_config
    )
    
    # Replace with mock model for testing
    engine.local_model = MockLocalModelInterface(local_model_config)
    
    # Test 1: Task analysis with mock local model
    print("Test 1: Task Analysis with Mock Local Model")
    task = "分析这份报告的主要观点，并提供改进建议"
    analysis = engine.analyze_task(task)
    print(f"Task type: {analysis['task_type']}")
    print(f"Privacy risk level: {analysis['privacy_risk_level']}")
    print(f"Recommended strategy: {analysis['recommended_strategy']}")
    
    if 'local_model_analysis' in analysis:
        print("\nEnhanced analysis from mock local model:")
        print(f"Enhanced task type: {analysis['enhanced_task_type']}")
        print(f"Enhanced complexity: {analysis['enhanced_complexity']}")
        print(f"Recommended strategy: {analysis['local_model_analysis'].get('recommended_strategy')}")
    else:
        print("\nLocal model not available, using default analysis")
    print()
    
    # Test 2: Simple task execution
    print("Test 2: Task Execution")
    simple_task = "总结人工智能的主要应用领域"
    result = engine.execute_sync(simple_task)
    
    print(f"Execution success: {result.success}")
    print(f"Execution time: {result.execution_time:.2f}s")
    print(f"Local model used: {result.metadata.get('local_model_used', False)}")
    print(f"Split strategy used: {result.metadata.get('split_strategy_used', 'auto')}")
    
    if result.success:
        print("\nFinal result:")
        print(result.final_result)
    else:
        print(f"\nError: {result.final_result}")
    print()
    
    # Test 3: Privacy protection with mock local model
    print("Test 3: Privacy Protection")
    private_task = "分析张三（电话13812345678，邮箱zhangsan@test.com）的客户反馈"
    privacy_result = engine.execute_sync(private_task)
    
    print(f"Execution success: {privacy_result.success}")
    if privacy_result.privacy_report:
        print(f"Privacy risk level: {privacy_result.privacy_report.get('risk_level', 'unknown')}")
        print(f"Total sensitive items detected: {privacy_result.privacy_report.get('total_detected', 0)}")
        print(f"Items by type: {privacy_result.privacy_report.get('items_by_type', {})}")
        
        if 'enhanced_analysis' in privacy_result.privacy_report:
            enhanced = privacy_result.privacy_report['enhanced_analysis']
            if 'local_pii_detection' in enhanced:
                print("\nEnhanced PII detection from mock local model:")
                for item in enhanced['local_pii_detection']:
                    print(f"- {item.get('type')}: {item.get('value')} (confidence: {item.get('confidence', 0):.2f})")
    print()
    
    # Test 4: Complex task with semantic splitting
    print("Test 4: Complex Task with Semantic Splitting")
    complex_task = "分析以下三个方面：1. 人工智能的发展趋势 2. 机器学习的应用场景 3. 深度学习的挑战"
    complex_result = engine.execute_sync(complex_task, split_strategy="semantic")
    
    print(f"Execution success: {complex_result.success}")
    print(f"Split strategy used: {complex_result.metadata.get('split_strategy_used', 'auto')}")
    
    if complex_result.success:
        print("\nFinal result:")
        print(complex_result.final_result)
    else:
        print(f"\nError: {complex_result.final_result}")
    print()
    
    # Test 5: Preview split with mock local model
    print("Test 5: Task Split Preview")
    preview = engine.preview_split(complex_task)
    
    print(f"Original task: {preview['original_task']}")
    print(f"Task type: {preview['task_type']}")
    print(f"Split strategy: {preview['split_strategy']}")
    print(f"Total subtasks: {preview['total_subtasks']}")
    
    print("\nSubtasks:")
    for subtask in preview['subtasks']:
        print(f"- {subtask['id']}: {subtask['description']}")
        print(f"  Type: {subtask['task_type']}")
        print(f"  Input preview: {subtask['input_preview']}")
        print(f"  Sensitive info count: {subtask['sensitive_info_count']}")
        print()
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    main()
