# SplitMind Core

[![PyPI version](https://badge.fury.io/py/splitmind-core.svg)](https://badge.fury.io/py/splitmind-core)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Privacy-first text processing library - Zero external dependencies (except pydantic)**

SplitMind Core provides essential privacy protection capabilities for detecting and redacting sensitive information in text. It's designed to be lightweight, fast, and easy to integrate into any Python project.

## ✨ Features

- 🔒 **Sensitive Data Detection** - Automatically identify PII (Personally Identifiable Information)
- 🛡️ **Smart Redaction** - Replace sensitive data with placeholders
- 🔄 **Restoration Support** - Restore original data when needed
- 📊 **Risk Assessment** - Get privacy risk scores and reports
- 🚀 **Zero Config** - Works out of the box
- ⚡ **Pure Python** - Only depends on pydantic

## 🚀 Quick Start

```bash
pip install splitmind-core
```

```python
from splitmind_core import PrivacyHandler

# Initialize handler
handler = PrivacyHandler()

# Detect and redact sensitive information
text = "Contact: John Doe, Phone: 13812345678, Email: john@example.com"
redacted, mapping = handler.redact(text)

print(redacted)
# Output: Contact: [REDACTED_NAME_1], Phone: [REDACTED_PHONE_1], Email: [REDACTED_EMAIL_1]

# Generate privacy report
report = handler.generate_report(text)
print(f"Risk Level: {report.risk_level}")
print(f"Items Detected: {report.total_items_detected}")
```

## 📋 Supported Data Types

| Type | Example | Detection |
|------|---------|-----------|
| Phone | 13812345678 | ✅ Mobile & landline |
| Email | user@example.com | ✅ All formats |
| ID Card | 320123199001011234 | ✅ Chinese ID |
| Bank Card | 6222 0222 0000 0000 000 | ✅ Credit/Debit |
| Passport | E12345678 | ✅ Multiple countries |
| Amount | ¥1,000.00 | ✅ Currency detection |
| IP Address | 192.168.1.1 | ✅ IPv4 |
| URL | https://example.com | ✅ Web links |

## 🛠️ Advanced Usage

### Custom Patterns

```python
from splitmind_core import PrivacyHandler

handler = PrivacyHandler()

# Add custom pattern
handler.add_custom_pattern("employee_id", r"EMP-\d{6}")

# Use it
text = "Employee: EMP-123456"
redacted, mapping = handler.redact(text)
```

### Partial Masking

```python
# Mask with asterisks instead of full redaction
masked, mapping = handler.mask_partial(text, mask_char="*")
# Result: Phone: 138****5678
```

### Risk Assessment

```python
report = handler.generate_report(text)

print(f"Risk Level: {report.risk_level}")  # low, medium, high, critical
print(f"Risk Score: {len(report.sensitive_items)}")

for item in report.sensitive_items:
    print(f"- {item.info_type}: {item.original_value}")
```

## 📦 Installation

```bash
# Basic installation
pip install splitmind-core

# With development tools
pip install splitmind-core[dev]
```

## 🔗 Related Packages

- [`splitmind`](https://pypi.org/project/splitmind/) - Full package with all features
- [`splitmind-cli`](https://pypi.org/project/splitmind-cli/) - Command line interface
- [`splitmind-providers`](https://pypi.org/project/splitmind-providers/) - AI provider adapters

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/yourusername/splitmind/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for privacy-first AI interactions
- Built with ❤️ by the SplitMind team
