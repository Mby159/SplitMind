# SplitMind Providers

AI provider integrations for SplitMind - Privacy-preserving multi-agent task orchestration.

## Installation

### Base installation (core functionality only)

```bash
pip install splitmind-providers
```

### With specific providers

```bash
# OpenAI only
pip install splitmind-providers[openai]

# Anthropic only  
pip install splitmind-providers[anthropic]

# Kimi only
pip install splitmind-providers[kimi]

# Local models (Ollama)
pip install splitmind-providers[local]

# All providers
pip install splitmind-providers[all]
```

## Available Providers

### 1. Local Provider
- **Models**: llama3.2:3b, llama3.2:1b, gemma3:1b, qwen2.5:3b, qwen2.5-coder:1.5b, olmo2:7b
- **Capabilities**: chat, completion
- **Max Tokens**: 32,768
- **Description**: Locally deployed models via Ollama, LM Studio, or any OpenAI-compatible server

### 2. OpenAI Provider
- **Models**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, gpt-3.5-turbo-16k
- **Capabilities**: chat, completion, vision, function_calling
- **Max Tokens**: 16,384
- **Description**: OpenAI's GPT models

### 3. Anthropic Provider (Claude)
- **Models**: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240229, claude-2.1, claude-2.0
- **Capabilities**: chat, completion, vision, function_calling
- **Max Tokens**: 200,000
- **Description**: Anthropic's Claude models

### 4. Kimi Provider
- **Models**: kimi, kimi-pro, kimi-max, kimi-coder
- **Capabilities**: chat, completion, vision
- **Max Tokens**: 128,000
- **Description**: Kimi (Moonshot AI) models

## Usage

### Basic usage

```python
from splitmind_providers import OpenAIProvider, ProviderRegistry

# Create provider
provider = OpenAIProvider(api_key="your-api-key")

# Generate text
result = provider.generate(
    prompt="Write a poem about AI",
    system_prompt="You are a creative poet",
    task_type="generation"
)

print(result)
```

### Using the registry

```python
from splitmind_providers import ProviderRegistry, OpenAIProvider, AnthropicProvider

# Create registry
registry = ProviderRegistry()

# Register providers
registry.register_provider("openai", OpenAIProvider(api_key="your-key"))
registry.register_provider("anthropic", AnthropicProvider(api_key="your-key"))

# Get provider status
status = registry.get_provider_status()
print(status)

# Get best provider for task
best_provider = registry.get_best_provider(
    task_type="analysis",
    required_capabilities=["chat"]
)

if best_provider:
    result = best_provider.generate("Analyze this data...")
    print(result)
```

### Local models

```python
from splitmind_providers import LocalProvider

# Create local provider (defaults to llama3.2:3b)
provider = LocalProvider()

# Generate text using local model
result = provider.generate("Tell me a joke")
print(result)
```

## Configuration

All providers support the following configuration options:

- `api_key`: API key for cloud providers
- `base_url`: Custom API endpoint URL
- `model`: Model name to use
- `config`: GenerationConfig object with temperature, max_tokens, etc.

## Requirements

- Python 3.9+
- splitmind-core>=0.1.0
- httpx>=0.27.0

## Optional Dependencies

- `openai>=1.0.0` (for OpenAI provider)
- `anthropic>=0.20.0` (for Anthropic provider)
- `psutil>=5.0.0` (for local provider system info)

## License

MIT
