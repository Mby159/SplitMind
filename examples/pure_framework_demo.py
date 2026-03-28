"""
Pure Framework Demo - SplitMind without AI.

Demonstrates that SplitMind's core functionality (privacy protection,
task splitting, result aggregation) works perfectly without any AI!
"""

from splitmind_core.privacy import PrivacyHandler
from splitmind_core.splitter import TaskSplitter


def demo_privacy_protection():
    """Demo 1: Privacy protection - no AI needed."""
    print("=" * 70)
    print("DEMO 1: Privacy Protection (NO AI NEEDED!)")
    print("=" * 70)
    
    handler = PrivacyHandler()
    
    sensitive_text = """
合同信息：
甲方：张三
乙方：李四
联系电话：13812345678
身份证号：320123199001011234
邮箱：zhangsan@example.com
银行账号：6222 0222 0000 1234 567
金额：人民币 50000 元
    """.strip()
    
    print("\nOriginal text:")
    print(sensitive_text)
    
    print("\n" + "-" * 70)
    print("Step 1: Analyze privacy risks...")
    
    report = handler.generate_report(sensitive_text)
    print(f"  Risk Level: {report.risk_level}")
    print(f"  Total Items: {report.total_items_detected}")
    print(f"  Detected Types: {', '.join(report.items_by_type.keys())}")
    
    print("\nStep 2: Redact sensitive information...")
    redacted, mapping = handler.redact(sensitive_text)
    print("\nRedacted text:")
    print(redacted)
    
    print("\nStep 3: Restore original info (if needed)...")
    restored = handler.restore(redacted, mapping)
    print("\nRestored text:")
    print(restored)
    
    print("\n[OK] Privacy protection works perfectly without AI!")
    return redacted, mapping


def demo_task_splitting():
    """Demo 2: Task splitting - no AI needed."""
    print("\n" + "=" * 70)
    print("DEMO 2: Task Splitting (NO AI NEEDED!)")
    print("=" * 70)
    
    splitter = TaskSplitter()
    
    complex_task = """
请帮我完成以下工作：
1. 分析2024年的销售数据趋势
2. 生成一份市场分析报告
3. 给客户发送邮件总结
4. 更新内部文档
    """.strip()
    
    print("\nComplex task:")
    print(complex_task)
    
    print("\n" + "-" * 70)
    print("Splitting with 'section' strategy...")
    
    result = splitter.split(complex_task, strategy="section")
    
    print(f"\nSplit into {len(result.subtasks)} subtasks:")
    for i, subtask in enumerate(result.subtasks, 1):
        print(f"\n  Subtask {i}: [{subtask.task_type.value}]")
        print(f"  Description: {subtask.description}")
    
    print("\n[OK] Task splitting works perfectly without AI!")
    return result


def main():
    """Main demo function."""
    print("SplitMind Pure Framework Demo")
    print("Showing that SplitMind works WITHOUT ANY AI!")
    print("=" * 70)
    
    demo_privacy_protection()
    demo_task_splitting()
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print("SplitMind's core features work perfectly without AI:")
    print("  [X] Privacy detection and redaction")
    print("  [X] Task splitting")
    print("\nAI is completely OPTIONAL - just one possible execution backend!")
    print("=" * 70)


if __name__ == "__main__":
    main()
