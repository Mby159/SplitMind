#!/usr/bin/env python3
"""
Execution Modes Demo
Demonstrates the three execution modes of SplitMind:
- LOCAL_ONLY: All processing done locally (maximum privacy)
- HYBRID: Privacy protection local, execution can use online providers (balanced)
- ONLINE: Can use online services for splitting and execution (maximum capability)
"""

from splitmind.core.engine import SplitMindEngine, ExecutionConfig, ExecutionMode
from splitmind.core.local_model import LocalModelConfig, LocalModelBackend


def demo_local_only_mode():
    """Demonstrate LOCAL_ONLY execution mode."""
    print("=" * 70)
    print("MODE 1: LOCAL_ONLY (Maximum Privacy)")
    print("=" * 70)
    print("All processing is done locally. No data leaves your system.")
    print()
    
    # Create engine with LOCAL_ONLY mode
    config = ExecutionConfig(
        execution_mode=ExecutionMode.LOCAL_ONLY,
        enable_privacy_protection=True
    )
    
    engine = SplitMindEngine(config=config)
    
    # Analyze a task
    task = "分析张三（电话13812345678）的客户反馈"
    analysis = engine.analyze_task(task)
    
    print(f"Task: {task}")
    print(f"Execution Mode: {analysis['execution_mode']}")
    print(f"Privacy Risk Level: {analysis['privacy_risk_level']}")
    print(f"Sensitive Info Detected: {analysis['sensitive_info_detected']}")
    print()
    
    # Execute the task
    result = engine.execute_sync(task)
    
    print(f"Execution Success: {result.success}")
    print(f"Execution Mode Used: {result.metadata.get('execution_mode')}")
    print(f"Providers Used: {result.metadata.get('providers_used')}")
    print(f"Final Result: {result.final_result[:100]}...")
    print()


def demo_hybrid_mode():
    """Demonstrate HYBRID execution mode."""
    print("=" * 70)
    print("MODE 2: HYBRID (Balanced)")
    print("=" * 70)
    print("Privacy protection is done locally, execution can use online providers.")
    print("Sensitive data is redacted before sending to online AI services.")
    print()
    
    # Create engine with HYBRID mode (default)
    config = ExecutionConfig(
        execution_mode=ExecutionMode.HYBRID,
        enable_privacy_protection=True
    )
    
    engine = SplitMindEngine(config=config)
    
    # Analyze a task
    task = "总结人工智能的主要应用领域"
    analysis = engine.analyze_task(task)
    
    print(f"Task: {task}")
    print(f"Execution Mode: {analysis['execution_mode']}")
    print(f"Privacy Risk Level: {analysis['privacy_risk_level']}")
    print()
    
    # Execute the task
    result = engine.execute_sync(task)
    
    print(f"Execution Success: {result.success}")
    print(f"Execution Mode Used: {result.metadata.get('execution_mode')}")
    print(f"Providers Used: {result.metadata.get('providers_used')}")
    print(f"Final Result: {result.final_result[:100]}...")
    print()


def demo_online_mode():
    """Demonstrate ONLINE execution mode."""
    print("=" * 70)
    print("MODE 3: ONLINE (Maximum Capability)")
    print("=" * 70)
    print("Can use online AI services for both splitting and execution.")
    print("Provides the best results but requires internet connection.")
    print()
    
    # Create engine with ONLINE mode
    config = ExecutionConfig(
        execution_mode=ExecutionMode.ONLINE,
        enable_privacy_protection=True
    )
    
    engine = SplitMindEngine(config=config)
    
    # Analyze a task
    task = "分析以下三个方面：1. 人工智能的发展趋势 2. 机器学习的应用场景 3. 深度学习的挑战"
    analysis = engine.analyze_task(task)
    
    print(f"Task: {task}")
    print(f"Execution Mode: {analysis['execution_mode']}")
    print(f"Privacy Risk Level: {analysis['privacy_risk_level']}")
    print(f"Recommended Strategy: {analysis['recommended_strategy']}")
    print()
    
    # Preview task split
    preview = engine.preview_split(task)
    print(f"Split Strategy: {preview['split_strategy']}")
    print(f"Total Subtasks: {preview['total_subtasks']}")
    print()


def demo_mode_comparison():
    """Compare the three execution modes."""
    print("=" * 70)
    print("EXECUTION MODES COMPARISON")
    print("=" * 70)
    print()
    
    comparison = """
┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Feature         │ LOCAL_ONLY       │ HYBRID           │ ONLINE           │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Privacy         │ Maximum          │ High             │ Medium           │
│ Performance     │ Fast (local)     │ Balanced         │ Depends on API   │
│ Cost            │ Free             │ API costs        │ API costs        │
│ Internet        │ Not required     │ Required for     │ Required         │
│                 │                  │ execution        │                  │
│ Task Splitting  │ Local            │ Local            │ Can use online   │
│ Execution       │ Local            │ Can use online   │ Can use online   │
│ Best For        │ Sensitive data   │ General use      │ Complex tasks    │
└─────────────────┴──────────────────┴──────────────────┴──────────────────┘
    """
    print(comparison)
    print()


def main():
    print("=" * 70)
    print("SplitMind Execution Modes Demo")
    print("=" * 70)
    print()
    print("SplitMind now supports three execution modes, giving you the")
    print("flexibility to choose between privacy and capability based on")
    print("your specific needs.")
    print()
    
    demo_mode_comparison()
    demo_local_only_mode()
    demo_hybrid_mode()
    demo_online_mode()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print()
    print("You can choose the execution mode that best fits your needs:")
    print("- Use LOCAL_ONLY for maximum privacy protection")
    print("- Use HYBRID for a balance of privacy and capability")
    print("- Use ONLINE for maximum AI capability")
    print()


if __name__ == "__main__":
    main()
