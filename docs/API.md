# SplitMind API 文档

## 概述

SplitMind 提供了一套完整的 API，用于隐私保护的多代理任务编排。本文档详细介绍了核心功能的使用方法。

## 核心模块

### 1. PrivacyHandler

#### 功能：
- 检测和处理敏感信息
- 风险评估和分类
- 敏感信息还原

#### 使用示例：

```python
from splitmind.core.privacy import PrivacyHandler

# 创建隐私处理器
privacy_handler = PrivacyHandler()

# 检测敏感信息
text = "我的邮箱是 example@example.com，电话号码是 13800138000"
sensitive_info = privacy_handler.detect_sensitive_info(text)
print(sensitive_info)

# 脱敏处理
redacted_text, mappings = privacy_handler.redact_sensitive_info(text)
print(redacted_text)

# 还原敏感信息
restored_text = privacy_handler.restore_sensitive_info(redacted_text, mappings)
print(restored_text)

# 评估风险
risk_level = privacy_handler.assess_risk(text)
print(f"Risk level: {risk_level}")
```

### 2. TaskSplitter

#### 功能：
- 任务拆分策略
- 语义单元提取
- 依赖管理

#### 使用示例：

```python
from splitmind.core.splitter import TaskSplitter

# 创建任务拆分器
task_splitter = TaskSplitter()

# 拆分任务
task = "请分析这份财务报告，提取关键指标并生成摘要"
strategy = "semantic"  # auto, single, section, semantic, parallel, dependency
subtasks = task_splitter.split_task(task, strategy=strategy)

for i, subtask in enumerate(subtasks):
    print(f"Subtask {i+1}: {subtask.content}")
    if subtask.dependencies:
        print(f"  Dependencies: {subtask.dependencies}")

# 计算执行顺序
execution_order = task_splitter.calculate_execution_order(subtasks)
print(f"Execution order: {execution_order}")
```

### 3. ResultAggregator

#### 功能：
- 结果聚合策略
- 质量评估
- 冲突检测

#### 使用示例：

```python
from splitmind.core.aggregator import ResultAggregator
from splitmind.core.splitter import SubTaskResult

# 创建结果聚合器
aggregator = ResultAggregator()

# 模拟子任务结果
results = [
    SubTaskResult(task_id="1", content="分析显示收入增长 10%"),
    SubTaskResult(task_id="2", content="利润提升 15%"),
    SubTaskResult(task_id="3", content="建议增加市场投入")
]

# 聚合结果
strategy = "hierarchical"  # sequential, parallel_merge, hierarchical, voting, best_of, consensus
aggregated_result = aggregator.aggregate(results, strategy=strategy)
print(aggregated_result)

# 评估结果质量
quality = aggregator.assess_quality(aggregated_result)
print(f"Result quality: {quality}")

# 检测冲突
conflicts = aggregator.detect_conflicts(results)
if conflicts:
    print("Conflicts detected:")
    for conflict in conflicts:
        print(f"  {conflict}")
```

### 4. ProviderRegistry

#### 功能：
- 管理 AI 提供商
- 自动发现和注册
- 提供商选择

#### 使用示例：

```python
from splitmind.providers import registry

# 列出可用提供商
providers = registry.list_providers()
print(f"Available providers: {providers}")

# 获取提供商信息
info = registry.get_all_info()
for name, provider_info in info.items():
    print(f"{name}: {provider_info.description}")

# 创建提供商实例
local_provider = registry.create_provider("local")
openai_provider = registry.create_provider("openai", api_key="your-api-key")

# 选择最佳提供商
best_provider = registry.select_best_provider(
    task_type="analysis",
    require_capability="chat"
)
print(f"Best provider for analysis: {best_provider}")

# 注册自定义提供商
from splitmind.providers import BaseProvider, register_provider
from splitmind.providers.base import ProviderInfo, ProviderCapability

class MyProvider(BaseProvider):
    def _default_model(self):
        return "my-model"
    
    def get_info(self):
        return ProviderInfo(
            name="my-provider",
            description="My custom provider",
            models=["my-model"],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096
        )
    
    def generate(self, prompt, system_prompt=None, task_type=None, **kwargs):
        return f"Response: {prompt}"
    
    async def generate_async(self, prompt, system_prompt=None, task_type=None, **kwargs):
        return f"Response: {prompt}"

# 注册自定义提供商
register_provider(MyProvider)

# 创建自定义提供商实例
my_provider = registry.create_provider("MyProvider")
```

### 5. LocalModelInterface

#### 功能：
- 本地模型交互
- 支持 Ollama 后端
- 文本生成和分类

#### 使用示例：

```python
from splitmind.core.local_model import LocalModelInterface

# 创建本地模型接口
local_model = LocalModelInterface(model="llama3.2:3b")

# 生成文本
response = local_model.generate("Hello, how are you?")
print(response)

# 异步生成文本
import asyncio

async def generate_async():
    response = await local_model.generate_async("Hello, how are you?")
    print(response)

asyncio.run(generate_async())

# 分类文本
classification = local_model.classify("This is a test", labels=["positive", "negative", "neutral"])
print(classification)

# 检测敏感信息
pii_detection = local_model.detect_pii("My email is example@example.com")
print(pii_detection)

# 合并结果
results = ["Result 1", "Result 2", "Result 3"]
merged = local_model.merge_results(results)
print(merged)
```

### 6. Engine

#### 功能：
- 主编排引擎
- 执行模式管理
- 完整的任务处理流程

#### 使用示例：

```python
from splitmind.core.engine import Engine, ExecutionMode

# 创建引擎
engine = Engine(execution_mode=ExecutionMode.HYBRID)

# 处理任务
task = "请分析这份财务报告，提取关键指标并生成摘要"
result = engine.process_task(task)
print(result)

# 异步处理任务
import asyncio

async def process_task_async():
    result = await engine.process_task_async(task)
    print(result)

asyncio.run(process_task_async())

# 更改执行模式
engine.set_execution_mode(ExecutionMode.LOCAL_ONLY)
result = engine.process_task(task)
print(result)
```

## 配置管理

### ConfigManager

#### 功能：
- 配置持久化
- 执行模式管理
- 默认模型设置

#### 使用示例：

```python
from splitmind.config import config_manager, Settings

# 加载配置
config = config_manager.load()
print(f"Execution mode: {config.execution_mode}")
print(f"Default model: {config.default_model}")

# 保存配置
config.execution_mode = "online"
config.default_model = "llama3.2:7b"
config_manager.save(config)

# 获取执行模式
from splitmind.core.engine import ExecutionMode
mode = config_manager.get_execution_mode()
print(f"Current execution mode: {mode}")

# 设置执行模式
config_manager.set_execution_mode(ExecutionMode.HYBRID)

# 获取环境设置
print(f"OpenAI API key: {Settings().openai_api_key}")
print(f"Local model URL: {Settings().local_model_url}")
```

## 命令行接口

### 基本用法

```bash
# 处理任务
splitmind "请分析这份财务报告"

# 指定执行模式
splitmind "请分析这份财务报告" --mode hybrid

# 指定策略
splitmind "请分析这份财务报告" --strategy semantic

# 帮助信息
splitmind --help
```

### 命令行选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--mode` | 执行模式 (local, hybrid, online) | hybrid |
| `--strategy` | 任务拆分策略 (auto, single, section, semantic, parallel, dependency) | auto |
| `--aggregator` | 结果聚合策略 (sequential, parallel_merge, hierarchical, voting, best_of, consensus) | hierarchical |
| `--model` | 本地模型名称 | llama3.2:3b |
| `--help` | 显示帮助信息 | - |

## Web 界面

### 访问方式

启动 Web 服务：

```bash
python -m splitmind.web.app
```

然后访问 `http://localhost:8000`

### 功能

- 任务输入和处理
- 执行模式选择
- 实时执行状态
- 结果展示

## 插件系统

### 创建插件

1. **创建项目结构**

```
splitmind-custom-provider/
├── splitmind_custom_provider/
│   ├── __init__.py
│   └── custom_provider.py
└── setup.py
```

2. **实现提供商**

```python
# splitmind_custom_provider/custom_provider.py
from splitmind.providers import BaseProvider, ProviderInfo, ProviderCapability

class CustomProvider(BaseProvider):
    def _default_model(self):
        return "custom-model"
    
    def get_info(self):
        return ProviderInfo(
            name="custom",
            description="Custom provider",
            models=["custom-model"],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096
        )
    
    def generate(self, prompt, system_prompt=None, task_type=None, **kwargs):
        return f"Custom response: {prompt}"
    
    async def generate_async(self, prompt, system_prompt=None, task_type=None, **kwargs):
        return f"Custom response: {prompt}"
```

3. **配置 setup.py**

```python
from setuptools import setup, find_packages

setup(
    name="splitmind-custom-provider",
    version="0.1.0",
    description="Custom provider plugin for SplitMind",
    packages=find_packages(),
    install_requires=["splitmind"],
    entry_points={
        'splitmind.provider': [
            'custom = splitmind_custom_provider.custom_provider:CustomProvider'
        ]
    }
)
```

4. **安装和使用**

```bash
pip install -e .
```

然后 SplitMind 会自动发现并注册该插件。

## 执行模式

### LOCAL_ONLY
- 仅使用本地模型
- 最高隐私保护
- 适合处理敏感信息

### HYBRID
- 优先使用本地模型
- 复杂任务使用在线模型
- 平衡隐私和能力

### ONLINE
- 使用在线模型
- 最高处理能力
- 适合非敏感任务

## 最佳实践

1. **隐私保护**
   - 对于敏感信息，使用 LOCAL_ONLY 模式
   - 利用 PrivacyHandler 进行敏感信息检测和处理

2. **性能优化**
   - 对于简单任务，使用 single 或 section 策略
   - 对于复杂任务，使用 semantic 或 dependency 策略

3. **提供商选择**
   - 根据任务类型选择合适的提供商
   - 利用 registry.select_best_provider() 自动选择

4. **错误处理**
   - 实现适当的错误处理和重试机制
   - 监控提供商可用性

5. **扩展性**
   - 使用插件系统添加自定义提供商
   - 扩展核心功能通过继承基类

## 故障排除

### 常见问题

1. **提供商连接失败**
   - 检查 API 密钥是否正确
   - 验证网络连接
   - 检查提供商服务状态

2. **本地模型启动失败**
   - 确保 Ollama 服务正在运行
   - 检查模型是否已下载
   - 验证本地模型 URL 配置

3. **任务拆分失败**
   - 检查任务描述是否清晰
   - 尝试使用不同的拆分策略
   - 检查输入文本长度

4. **结果聚合异常**
   - 检查子任务结果格式
   - 尝试使用不同的聚合策略
   - 验证子任务依赖关系

### 日志和调试

- 启用详细日志：`export SPLITMIND_LOG_LEVEL=DEBUG`
- 检查 Web 界面的执行状态
- 查看提供商状态：`registry.get_provider_status()`

## 版本兼容性

- Python 3.9+
- 依赖包版本见 pyproject.toml

## 未来计划

- 更多提供商支持
- 高级任务拆分策略
- 智能结果聚合
- 企业级功能

---

**最后更新**：2026-03-30
