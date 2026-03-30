# 测试指南

本文档提供了 SplitMind 项目的测试指南，包括如何编写、运行和维护测试。

## 目录

- [测试指南](#测试指南)
  - [目录](#目录)
  - [测试架构](#测试架构)
  - [测试类型](#测试类型)
  - [测试目录结构](#测试目录结构)
  - [编写测试](#编写测试)
  - [运行测试](#运行测试)
  - [测试覆盖率](#测试覆盖率)
  - [测试最佳实践](#测试最佳实践)
  - [Mock 和 Stub](#mock-和-stub)
  - [CI/CD 测试](#cicd-测试)
  - [故障排除](#故障排除)

## 测试架构

SplitMind 使用以下测试架构：

- **单元测试**：测试单个组件的功能
- **集成测试**：测试组件之间的交互
- **端到端测试**：测试完整的工作流程

## 测试类型

### 1. 单元测试

- **目标**：测试单个函数、方法或类
- **范围**：最小化，专注于特定功能
- **依赖**：通常使用 mock 或 stub 来隔离依赖
- **执行速度**：快速

### 2. 集成测试

- **目标**：测试多个组件的交互
- **范围**：跨越多个模块
- **依赖**：可能使用真实的依赖或部分 mock
- **执行速度**：中等

### 3. 端到端测试

- **目标**：测试完整的工作流程
- **范围**：整个应用程序
- **依赖**：使用真实的依赖
- **执行速度**：较慢

## 测试目录结构

SplitMind 项目的测试目录结构如下：

```
tests/
├── test_core.py             # 核心功能测试
├── test_providers.py        # 提供商测试
├── test_engine.py           # 引擎测试
├── test_config.py           # 配置测试
├── integration/             # 集成测试
│   ├── test_integration.py  # 集成测试
│   └── ...
└── conftest.py              # 测试配置
```

## 编写测试

### 1. 单元测试示例

```python
# tests/test_core.py
import pytest
from splitmind.core.privacy import PrivacyHandler

def test_privacy_handler_detect_sensitive_info():
    """测试隐私处理器检测敏感信息的功能"""
    privacy_handler = PrivacyHandler()
    text = "我的邮箱是 example@example.com，电话号码是 13800138000"
    sensitive_info = privacy_handler.detect_sensitive_info(text)
    
    assert len(sensitive_info) > 0
    assert any(info['type'] == 'email' for info in sensitive_info)
    assert any(info['type'] == 'phone' for info in sensitive_info)

def test_privacy_handler_redact_sensitive_info():
    """测试隐私处理器脱敏处理的功能"""
    privacy_handler = PrivacyHandler()
    text = "我的邮箱是 example@example.com"
    redacted_text, mappings = privacy_handler.redact_sensitive_info(text)
    
    assert "[EMAIL_0]" in redacted_text
    assert "example@example.com" not in redacted_text
    assert len(mappings) == 1

def test_privacy_handler_restore_sensitive_info():
    """测试隐私处理器还原敏感信息的功能"""
    privacy_handler = PrivacyHandler()
    text = "我的邮箱是 example@example.com"
    redacted_text, mappings = privacy_handler.redact_sensitive_info(text)
    restored_text = privacy_handler.restore_sensitive_info(redacted_text, mappings)
    
    assert restored_text == text
```

### 2. 集成测试示例

```python
# tests/integration/test_integration.py
import pytest
from splitmind.core.engine import Engine, ExecutionMode

def test_engine_process_task():
    """测试引擎处理任务的功能"""
    engine = Engine(execution_mode=ExecutionMode.LOCAL_ONLY)
    task = "请告诉我 1 + 1 等于多少"
    result = engine.process_task(task)
    
    assert result is not None
    assert isinstance(result, str)
    assert "2" in result
```

### 3. 测试最佳实践

1. **测试命名**
   - 测试函数名应该清晰描述测试内容
   - 使用 `test_` 前缀
   - 对于类测试，使用 `Test` 前缀

2. **测试结构**
   - 使用 Arrange-Act-Assert 模式
   - 每个测试应该测试一个特定功能
   - 测试应该是独立的

3. **测试覆盖**
   - 测试正常情况
   - 测试边缘情况
   - 测试异常情况

4. **测试数据**
   - 使用有意义的测试数据
   - 避免硬编码测试数据
   - 考虑使用测试数据工厂

## 运行测试

### 1. 运行所有测试

```bash
pytest tests/ -v
```

### 2. 运行特定测试文件

```bash
pytest tests/test_core.py -v
```

### 3. 运行特定测试函数

```bash
pytest tests/test_core.py::test_privacy_handler_detect_sensitive_info -v
```

### 4. 运行集成测试

```bash
pytest tests/integration/ -v
```

### 5. 并行运行测试

```bash
pytest tests/ -v -n auto
```

## 测试覆盖率

### 1. 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=splitmind

# 生成 HTML 覆盖率报告
pytest tests/ --cov=splitmind --cov-report=html

# 生成 XML 覆盖率报告（用于 CI）
pytest tests/ --cov=splitmind --cov-report=xml
```

### 2. 查看覆盖率报告

- **终端报告**：直接在终端查看
- **HTML 报告**：打开 `htmlcov/index.html`
- **XML 报告**：用于 CI 系统

### 3. 覆盖率目标

- **核心功能**：≥ 80%
- **关键模块**：≥ 70%
- **整体**：≥ 60%

## 测试最佳实践

### 1. 隔离测试

- 使用 mock 或 stub 隔离外部依赖
- 避免测试依赖于外部服务
- 确保测试可以在任何环境中运行

### 2. 测试速度

- 单元测试应该快速执行
- 集成测试可以稍微慢一些
- 端到端测试可以更慢，但应该控制在合理范围内

### 3. 测试维护

- 定期运行测试
- 当代码更改时更新测试
- 移除过时的测试
- 保持测试代码的质量

### 4. 测试文档

- 为复杂的测试添加注释
- 解释测试的目的和预期行为
- 记录测试的边缘情况

## Mock 和 Stub

### 1. 使用 unittest.mock

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """使用 mock 测试"""
    # 创建 mock 对象
    mock_provider = Mock()
    mock_provider.generate.return_value = "Mock response"
    
    # 使用 mock 对象
    result = mock_provider.generate("Test prompt")
    assert result == "Mock response"
    mock_provider.generate.assert_called_once_with("Test prompt")

def test_with_patch():
    """使用 patch 测试"""
    with patch('splitmind.providers.registry.create_provider') as mock_create:
        # 配置 mock
        mock_provider = Mock()
        mock_provider.generate.return_value = "Mock response"
        mock_create.return_value = mock_provider
        
        # 测试代码
        from splitmind.providers import registry
        provider = registry.create_provider("test")
        result = provider.generate("Test prompt")
        
        assert result == "Mock response"
        mock_create.assert_called_once_with("test")
```

### 2. 常见 Mock 场景

- **外部 API 调用**：Mock HTTP 请求
- **文件操作**：Mock 文件读写
- **时间依赖**：Mock 时间函数
- **随机值**：Mock 随机函数

## CI/CD 测试

### 1. GitHub Actions 配置

SplitMind 使用 GitHub Actions 进行 CI/CD 测试。配置文件位于 `.github/workflows/ci.yml`。

### 2. CI 测试流程

1. **代码检查**：运行 ruff、black、mypy
2. **单元测试**：运行所有单元测试
3. **集成测试**：运行集成测试
4. **覆盖率报告**：上传覆盖率报告到 Codecov

### 3. 本地 CI 测试

```bash
# 运行代码检查
ruff check splitmind
black --check splitmind
mypy splitmind

# 运行测试
pytest tests/ -v --cov=splitmind
```

## 故障排除

### 1. 测试失败

- **查看错误信息**：仔细阅读错误信息
- **重现问题**：尝试手动重现问题
- **检查测试数据**：确保测试数据正确
- **检查依赖**：确保所有依赖都已安装

### 2. 测试缓慢

- **识别缓慢的测试**：使用 `pytest --durations=10`
- **优化测试**：减少测试中的 I/O 操作
- **使用 mock**：避免真实的外部调用
- **并行运行**：使用 `-n auto` 并行运行测试

### 3. 测试覆盖率低

- **识别未覆盖的代码**：查看覆盖率报告
- **添加测试**：为未覆盖的代码添加测试
- **优化测试**：确保测试覆盖所有重要路径

### 4. 测试环境问题

- **虚拟环境**：确保使用正确的虚拟环境
- **依赖版本**：确保依赖版本一致
- **环境变量**：确保设置了必要的环境变量
- **网络连接**：对于需要网络的测试，确保网络连接正常

---

**最后更新**：2026-03-30
