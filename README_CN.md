# SplitMind

**隐私优先的多智能体任务编排系统**

SplitMind 是一个创新的 AI 任务编排框架，通过任务拆分实现隐私保护，将任务分配给多个不同的 AI 提供商，最后汇总输出结果。

[English](README.md) | 中文

## 核心特性

- 🔒 **隐私保护**：自动检测并脱敏敏感信息（电话、邮箱、身份证等）
- 🧩 **智能拆分**：自动分析任务并拆分为独立子任务
- 🔀 **多提供商支持**：支持 OpenAI、Anthropic Claude、Kimi、本地模型等
- ⚡ **并行执行**：子任务并行执行，提升效率
- 🔄 **结果汇总**：多种策略汇总多个 AI 的结果
- 💻 **多种使用方式**：SDK、CLI、Web 界面

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    用户原始任务                          │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│              1. 隐私分析 & 敏感信息脱敏                   │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│              2. 任务拆分引擎                             │
└─────────────────────────┬───────────────────────────────┘
                          ▼
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   子任务 A     │ │   子任务 B     │ │   子任务 C     │
│   ↓           │ │   ↓           │ │   ↓           │
│  OpenAI       │ │   Claude      │ │    Kimi       │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        └─────────────────┼─────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│              3. 结果汇总 & 敏感信息还原                   │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    最终输出                              │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 安装

```bash
pip install splitmind
```

### 配置

复制配置文件并填入 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
KIMI_API_KEY=your-key
```

### SDK 使用

```python
import asyncio
from splitmind import SplitMindEngine
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider

async def main():
    # 创建引擎并注册提供商
    engine = SplitMindEngine(providers=[
        OpenAIProvider(api_key="your-key"),
        AnthropicProvider(api_key="your-key"),
    ])
    
    # 执行任务
    result = await engine.execute(
        task="分析这份报告的关键信息",
        context="报告内容...",
        strategy="parallel",
    )
    
    print(result.final_result)

asyncio.run(main())
```

### CLI 使用

```bash
# 执行任务
splitmind run "分析这份报告" --strategy parallel

# 从文件读取任务
splitmind run --file task.txt --output result.txt

# 预览任务拆分
splitmind preview "你的任务"

# 分析隐私风险
splitmind analyze "包含敏感信息的文本"

# 查看可用提供商
splitmind providers

# 启动 Web 服务
splitmind serve --port 8000

# 查看当前配置
splitmind config show

# 设置默认执行模式
splitmind config set-mode hybrid

# 设置默认本地模型
splitmind config set-model llama3.2:3b

# 启用/禁用隐私保护
splitmind config set-privacy true
```

### Web 界面

```bash
splitmind serve
```

访问 http://localhost:8000 使用可视化界面。

## 核心组件

### 1. 任务拆分器 (TaskSplitter)

```python
from splitmind.core.splitter import TaskSplitter

splitter = TaskSplitter()

# 分析任务类型
task_type = splitter.analyze_task_type("请分析这份报告")

# 检测敏感信息
sensitive = splitter.detect_sensitive_info("张三的电话是13812345678")

# 拆分任务
result = splitter.split("复杂任务...", strategy="parallel")
```

### 2. 隐私处理器 (PrivacyHandler)

```python
from splitmind.core.privacy import PrivacyHandler

handler = PrivacyHandler()

# 检测敏感信息
detected = handler.detect("联系方式：13812345678")

# 脱敏处理
redacted, mapping = handler.redact("张三的电话是13812345678")

# 还原敏感信息
restored = handler.restore(redacted, mapping)

# 生成隐私报告
report = handler.generate_report("包含敏感信息的文本")
```

### 3. 结果聚合器 (ResultAggregator)

```python
from splitmind.core.aggregator import ResultAggregator, AggregationStrategy

aggregator = ResultAggregator(
    default_strategy=AggregationStrategy.PARALLEL_MERGE
)

# 聚合多个结果
aggregated = aggregator.aggregate([
    SubTaskResult(subtask_id="1", provider="openai", result="结果1"),
    SubTaskResult(subtask_id="2", provider="claude", result="结果2"),
])
```

### 4. AI 提供商

```python
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider
from splitmind.providers.kimi_provider import KimiProvider
from splitmind.providers.local_provider import LocalProvider

# OpenAI
openai = OpenAIProvider(api_key="key", model="gpt-4")

# Anthropic Claude
claude = AnthropicProvider(api_key="key", model="claude-3-opus")

# Kimi (月之暗面)
kimi = KimiProvider(api_key="key")

# 本地模型 (Ollama, LM Studio 等)
local = LocalProvider(model="llama3", base_url="http://localhost:11434/v1")
```

## 执行模式

SplitMind 支持三种执行模式，用户可以根据隐私需求和性能要求选择合适的模式：

| 模式 | 说明 | 隐私级别 | 能力级别 |
|------|------|----------|----------|
| `local_only` | 所有处理都在本地完成 | 最高 | 有限 |
| `hybrid` | 隐私保护在本地，执行可以使用在线提供商 | 高 | 高 |
| `online` | 可以使用在线服务进行拆分和执行 | 中 | 最高 |

### 执行模式示例

```bash
# 使用 LOCAL_ONLY 模式（最高隐私保护）
splitmind run --mode local_only "分析销售数据"

# 使用 HYBRID 模式（平衡隐私和能力）
splitmind run --mode hybrid "分析销售数据"

# 使用 ONLINE 模式（最高能力）
splitmind run --mode online "分析销售数据"
```

## 任务拆分策略

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `auto` | 自动选择最佳策略 | 默认选项 |
| `single` | 不拆分，单一任务 | 简单任务 |
| `section` | 按段落拆分 | 长文档处理 |
| `semantic` | 按语义单元拆分 | 复杂分析 |
| `parallel` | 并行多角度分析 | 隐私敏感任务 |

## 结果聚合策略

| 策略 | 说明 |
|------|------|
| `sequential` | 按顺序组合结果 |
| `parallel_merge` | 并行合并，智能去重 |
| `hierarchical` | 层级整合，补充增强 |
| `voting` | 投票选择最佳答案 |
| `best_of` | 选择最高质量结果 |

## 支持的敏感信息类型

- 📱 电话号码
- 📧 电子邮箱
- 🪪 身份证号
- 💳 银行卡号
- 💰 金额
- 🌐 IP 地址
- 🔗 URL
- 📅 日期时间

## 开发

```bash
# 克隆仓库
git clone https://github.com/your-repo/splitmind.git
cd splitmind

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black splitmind
ruff check splitmind
```

## 贡献

欢迎贡献！请随时提交 Issue 或 PR。

### 简化维护说明
- **维护者**：你的名字（学生开发者）
- **响应时间**：我会尽量在周末查看 issues 和 PR
- **优先级**：Bug 修复 > 功能请求 > 文档

## 支持项目

如果 SplitMind 对你有帮助，考虑请我喝杯咖啡！☕

[Buy Me a Coffee](https://buymeacoffee.com/yourusername)

## 许可证

MIT License
