"""
SplitMind Example - Advanced usage with custom configuration.
"""

import asyncio
from splitmind import SplitMindEngine
from splitmind.core.splitter import TaskSplitter
from splitmind.core.aggregator import ResultAggregator, AggregationStrategy
from splitmind.core.privacy import PrivacyHandler
from splitmind.core.engine import ExecutionConfig
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider
from splitmind.providers.local_provider import LocalProvider


async def main():
    privacy_handler = PrivacyHandler(
        custom_patterns={
            "employee_id": r"EMP-\d{6}",
            "project_code": r"PRJ-[A-Z]{3}-\d{4}",
        },
        placeholder_format="[PROTECTED_{type}_{id}]",
    )
    
    task_splitter = TaskSplitter(
        enable_auto_redaction=True,
        llm_split=False,
    )
    
    result_aggregator = ResultAggregator(
        default_strategy=AggregationStrategy.HIERARCHICAL,
    )
    
    config = ExecutionConfig(
        max_concurrent_tasks=3,
        timeout_per_task=120,
        retry_failed_tasks=True,
        max_retries=2,
        enable_privacy_protection=True,
        default_strategy=AggregationStrategy.HIERARCHICAL,
    )
    
    providers = [
        LocalProvider(model="llama3"),
        LocalProvider(model="mistral", base_url="http://localhost:11434/v1"),
    ]
    
    engine = SplitMindEngine(
        providers=providers,
        config=config,
        privacy_handler=privacy_handler,
        task_splitter=task_splitter,
        result_aggregator=result_aggregator,
    )
    
    sensitive_document = """
    项目进度报告
    
    项目编号: PRJ-ABC-2024
    负责人: 李明 (工号: EMP-123456)
    
    本季度我们完成了以下工作:
    1. 用户调研: 访谈了50位客户，收集了200份问卷
    2. 产品开发: 完成了核心功能的开发
    3. 预算执行: 已使用预算150万元，剩余50万元
    
    下季度计划:
    - 完成产品测试
    - 准备市场推广
    - 招聘新团队成员
    
    联系方式: liming@company.com, 电话: 13987654321
    """
    
    print("=" * 60)
    print("隐私保护分析")
    print("=" * 60)
    
    report = privacy_handler.generate_report(sensitive_document)
    print(f"风险等级: {report.risk_level}")
    print(f"检测到的敏感信息数量: {report.total_items_detected}")
    print(f"按类型分布: {report.items_by_type}")
    
    print("\n" + "=" * 60)
    print("任务拆分预览")
    print("=" * 60)
    
    preview = engine.preview_split(sensitive_document, strategy="parallel")
    for subtask in preview["subtasks"]:
        print(f"\n子任务 {subtask['id']}:")
        print(f"  类型: {subtask['task_type']}")
        print(f"  描述: {subtask['description']}")
        print(f"  敏感信息数量: {subtask['sensitive_info_count']}")
    
    print("\n" + "=" * 60)
    print("执行任务")
    print("=" * 60)
    
    result = await engine.execute(
        task="请总结这份项目报告的关键信息",
        context=sensitive_document,
        split_strategy="parallel",
    )
    
    print(f"\n执行成功: {result.success}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    
    if result.privacy_report:
        print(f"隐私保护: 已处理 {result.privacy_report['total_detected']} 个敏感信息")
    
    print(f"\n最终结果:\n{result.final_result}")


async def custom_routing_example():
    print("\n" + "=" * 60)
    print("自定义路由示例")
    print("=" * 60)
    
    engine = SplitMindEngine(providers=[
        LocalProvider(model="llama3"),
    ])
    
    task = "分析以下数据并生成报告: 销售额增长20%，用户满意度提升15%"
    
    preview = engine.preview_split(task)
    
    print("任务将被拆分为以下子任务:")
    for st in preview["subtasks"]:
        print(f"  - {st['id']}: {st['description']}")
    
    result = await engine.execute(
        task=task,
        providers=["local"],
    )
    
    print(f"\n结果: {result.final_result}")


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(custom_routing_example())
