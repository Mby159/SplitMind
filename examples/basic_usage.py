"""
SplitMind Example - Basic usage demonstration.
"""

import asyncio
from splitmind import SplitMindEngine
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider
from splitmind.providers.kimi_provider import KimiProvider
from splitmind.providers.local_provider import LocalProvider


async def main():
    providers = []
    
    # providers.append(OpenAIProvider(api_key="your-openai-api-key"))
    # providers.append(AnthropicProvider(api_key="your-anthropic-api-key"))
    # providers.append(KimiProvider(api_key="your-kimi-api-key"))
    
    providers.append(LocalProvider(model="llama3"))
    
    engine = SplitMindEngine(providers=providers)
    
    task = """
    请分析以下客户反馈并提取关键信息：
    
    客户张三（电话：13812345678）反映他在2024年3月15日购买了价值2999元的产品，
    但收到的商品存在质量问题。他的邮箱是zhangsan@example.com，希望尽快处理退款。
    """
    
    print("=" * 60)
    print("任务分析预览")
    print("=" * 60)
    
    preview = engine.preview_split(task)
    print(f"任务类型: {preview['task_type']}")
    print(f"拆分策略: {preview['split_strategy']}")
    print(f"子任务数量: {preview['total_subtasks']}")
    
    print("\n" + "=" * 60)
    print("隐私分析")
    print("=" * 60)
    
    analysis = engine.analyze_task(task)
    print(f"隐私风险等级: {analysis['privacy_risk_level']}")
    print(f"检测到的敏感信息: {analysis['sensitive_info_detected']}")
    
    print("\n" + "=" * 60)
    print("执行任务")
    print("=" * 60)
    
    result = await engine.execute(task, strategy="parallel")
    
    print(f"\n执行成功: {result.success}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    print(f"\n最终结果:\n{result.final_result}")
    
    if result.aggregated_result:
        print(f"\n使用的AI提供商: {result.aggregated_result.providers_used}")
        print(f"置信度: {result.aggregated_result.confidence_score:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
