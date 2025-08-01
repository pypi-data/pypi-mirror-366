# Monkey Coder Core

Python orchestration core for AI-powered code generation and analysis.

## Features

- Multi-agent orchestration with SuperClaude, monkey1, and Gary8D systems
- Support for multiple AI providers (OpenAI, Anthropic, Google, Qwen)
- Real-time monitoring and metrics collection
- Comprehensive error tracking with Sentry
- Production-ready FastAPI backend

## Installation

```bash
pip install monkey-coder-core
```

## Usage

```python
from monkey_coder.app.main import app

# Run with uvicorn
# uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port 8000
```

## Model Support

The system only uses permitted models as defined in the MODEL_REGISTRY:

### OpenAI

- gpt-4.1
- gpt-4.1-mini

### Anthropic

- claude-4-opus
- claude-4-sonnet
- claude-3.7-sonnet
- claude-3.5-sonnet
- claude-3.5-haiku

### Google

- gemini-2.5-pro
- gemini-2.5-flash
- gemini-2.0-pro
- gemini-2.0-flash

### Qwen

- qwen-coder-3-32b
- qwen-coder-3-14b
- qwen-coder-3-7b
- qwen-coder-3-1.5b

### Grok

- grok-4
- grok-3

### Moonshot

- kimi-k2

## License

MIT License
