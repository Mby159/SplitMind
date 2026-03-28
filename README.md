# SplitMind

**Privacy-First Multi-Agent Task Orchestration System**

SplitMind is an innovative AI task orchestration framework that achieves privacy protection through task splitting, distributing tasks to multiple different AI providers, and finally aggregating the results.

English | [中文](README_CN.md)

## Core Features

- 🔒 **Privacy Protection**: Automatic detection and redaction of sensitive information (phone numbers, emails, ID cards, etc.)
- 🧩 **Intelligent Splitting**: Automatic task analysis and decomposition into independent subtasks
- 🔀 **Multi-Provider Support**: Support for OpenAI, Anthropic Claude, Kimi, local models, and more
- ⚡ **Parallel Execution**: Subtasks execute in parallel for improved efficiency
- 🔄 **Result Aggregation**: Multiple strategies for aggregating results from multiple AIs
- 💻 **Multiple Interfaces**: SDK, CLI, and Web interface

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User's Original Task                  │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│         1. Privacy Analysis & Sensitive Info Redaction   │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  2. Task Splitting Engine                │
└─────────────────────────┬───────────────────────────────┘
                          ▼
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Subtask A    │ │  Subtask B    │ │  Subtask C    │
│   ↓           │ │   ↓           │ │   ↓           │
│  OpenAI       │ │   Claude      │ │    Kimi       │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        └─────────────────┼─────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│       3. Result Aggregation & Sensitive Info Restore    │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Final Output                          │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
pip install splitmind
```

### Configuration

Copy the configuration file and fill in your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
KIMI_API_KEY=your-key
```

### SDK Usage

```python
import asyncio
from splitmind import SplitMindEngine
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider

async def main():
    # Create engine and register providers
    engine = SplitMindEngine(providers=[
        OpenAIProvider(api_key="your-key"),
        AnthropicProvider(api_key="your-key"),
    ])
    
    # Execute task
    result = await engine.execute(
        task="Analyze the key information in this report",
        context="Report content...",
        strategy="parallel",
    )
    
    print(result.final_result)

asyncio.run(main())
```

### CLI Usage

```bash
# Execute task
splitmind run "Analyze this report" --strategy parallel

# Read task from file
splitmind run --file task.txt --output result.txt

# Preview task splitting
splitmind preview "Your task"

# Analyze privacy risks
splitmind analyze "Text containing sensitive information"

# View available providers
splitmind providers

# Start web service
splitmind serve --port 8000

# View current configuration
splitmind config show

# Set default execution mode
splitmind config set-mode hybrid

# Set default local model
splitmind config set-model llama3.2:3b

# Enable/disable privacy protection
splitmind config set-privacy true
```

### Web Interface

```bash
splitmind serve
```

Visit http://localhost:8000 to use the visual interface.

## Core Components

### 1. TaskSplitter

```python
from splitmind.core.splitter import TaskSplitter

splitter = TaskSplitter()

# Analyze task type
task_type = splitter.analyze_task_type("Please analyze this report")

# Detect sensitive information
sensitive = splitter.detect_sensitive_info("John's phone is 13812345678")

# Split task
result = splitter.split("Complex task...", strategy="parallel")
```

### 2. PrivacyHandler

```python
from splitmind.core.privacy import PrivacyHandler

handler = PrivacyHandler()

# Detect sensitive information
detected = handler.detect("Contact: 13812345678")

# Redact sensitive information
redacted, mapping = handler.redact("John's phone is 13812345678")

# Restore sensitive information
restored = handler.restore(redacted, mapping)

# Generate privacy report
report = handler.generate_report("Text containing sensitive information")
```

### 3. ResultAggregator

```python
from splitmind.core.aggregator import ResultAggregator, AggregationStrategy

aggregator = ResultAggregator(
    default_strategy=AggregationStrategy.PARALLEL_MERGE
)

# Aggregate multiple results
aggregated = aggregator.aggregate([
    SubTaskResult(subtask_id="1", provider="openai", result="Result 1"),
    SubTaskResult(subtask_id="2", provider="claude", result="Result 2"),
])
```

### 4. AI Providers

```python
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider
from splitmind.providers.kimi_provider import KimiProvider
from splitmind.providers.local_provider import LocalProvider

# OpenAI
openai = OpenAIProvider(api_key="key", model="gpt-4")

# Anthropic Claude
claude = AnthropicProvider(api_key="key", model="claude-3-opus")

# Kimi (Moonshot AI)
kimi = KimiProvider(api_key="key")

# Local models (Ollama, LM Studio, etc.)
local = LocalProvider(model="llama3", base_url="http://localhost:11434/v1")
```

## Execution Modes

SplitMind supports three execution modes, allowing users to choose the appropriate mode based on privacy requirements and performance needs:

| Mode | Description | Privacy Level | Capability Level |
|------|-------------|---------------|------------------|
| `local_only` | All processing done locally | Highest | Limited |
| `hybrid` | Privacy protection local, execution can use online providers | High | High |
| `online` | Can use online services for splitting and execution | Medium | Highest |

### Execution Mode Examples

```bash
# Use LOCAL_ONLY mode (highest privacy protection)
splitmind run --mode local_only "Analyze sales data"

# Use HYBRID mode (balance privacy and capability)
splitmind run --mode hybrid "Analyze sales data"

# Use ONLINE mode (highest capability)
splitmind run --mode online "Analyze sales data"
```

## Task Splitting Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `auto` | Automatically select the best strategy | Default option |
| `single` | No splitting, single task | Simple tasks |
| `section` | Split by sections | Long document processing |
| `semantic` | Split by semantic units | Complex analysis |
| `parallel` | Parallel multi-angle analysis | Privacy-sensitive tasks |

## Result Aggregation Strategies

| Strategy | Description |
|----------|-------------|
| `sequential` | Combine results in order |
| `parallel_merge` | Parallel merge with intelligent deduplication |
| `hierarchical` | Hierarchical integration with enhancement |
| `voting` | Vote for the best answer |
| `best_of` | Select the highest quality result |

## Supported Sensitive Information Types

- 📱 Phone numbers
- 📧 Email addresses
- 🪪 ID card numbers
- 💳 Bank card numbers
- 💰 Monetary amounts
- 🌐 IP addresses
- 🔗 URLs
- 📅 Dates and times

## Development

```bash
# Clone repository
git clone https://github.com/your-repo/splitmind.git
cd splitmind

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black splitmind
ruff check splitmind
```

## Contributing

We welcome contributions! Please feel free to open issues or submit pull requests.

### Simplified Maintenance
- **Maintainer**: Your Name (Student Developer)
- **Response Time**: I'll try to review issues and PRs on weekends
- **Priority**: Bug fixes > Feature requests > Documentation

## Support the Project

If SplitMind has helped you, consider buying me a coffee! ☕

[Buy Me a Coffee](https://buymeacoffee.com/yourusername)

## License

MIT License
