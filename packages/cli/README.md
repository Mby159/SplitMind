# SplitMind CLI

Command line interface for SplitMind - Privacy-preserving multi-agent task orchestration.

## Installation

```bash
pip install splitmind-cli
```

This installs:
- `splitmind-core`: Core privacy and task orchestration
- `click`: Command line interface framework
- `rich`: Beautiful terminal output
- `python-dotenv`: Environment variable management

## Quick Start

### Demo (no API keys needed)

See SplitMind's privacy protection in action:

```bash
splitmind demo
```

With your own text:

```bash
splitmind demo "My phone is 13812345678 and email is test@example.com"
```

Generate a shareable report:

```bash
splitmind demo --share "sensitive text here"
```

### Analyze Text

Check text for sensitive information:

```bash
splitmind analyze "Text to analyze for PII"
```

### Redact Text

Remove sensitive information:

```bash
splitmind redact "Text with phone: 13812345678"
```

Save redacted text to a file:

```bash
splitmind redact "sensitive text" --output redacted.txt
```

## Commands

| Command | Description |
|---------|-------------|
| `demo` | Zero-config privacy demonstration |
| `analyze` | Analyze text for sensitive information |
| `redact` | Redact sensitive information from text |

## Privacy Protection

SplitMind detects and protects:
- Phone numbers (Chinese and international)
- Email addresses
- Chinese ID cards
- Passports
- Bank cards
- Credit cards
- Monetary amounts
- IP addresses
- URLs
- Dates and times

## License

MIT
