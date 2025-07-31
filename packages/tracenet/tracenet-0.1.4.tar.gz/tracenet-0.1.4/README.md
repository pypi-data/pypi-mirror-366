# Tracenet

A universal tracing middleware for agent applications with support for multiple tracing backends. This package provides automatic tracing setup - just import it and it works!

## Features

- 🔄 Zero-configuration setup - just import and go!
- 🤖 Automatic framework detection and integration
  - OpenAI Agents SDK
  - Google ADK
  - CrewAI
  - LangChain
- 🎯 Manual instrumentation if needed
- 🔌 Extensible backend system
- 🚀 Async/sync support

## Installation

```bash
pip install tracenet
```

## Quick Start

The simplest way to use tracenet is to just import it:

```python
# Just import the package - it automatically sets up tracing
import tracenet

# Your existing code will now be traced automatically!
```

If you need more control, you can use the manual instrumentation:

```python
from tracenet import trace, start_span, start_generation

# Optional: Use decorators for specific functions
@trace(name="my_function")
def my_function(arg1, arg2):
    return arg1 + arg2

# Optional: Use context managers for manual tracing
with start_span("manual_operation") as span:
    result = perform_operation()
    span.update(output=result)

# Optional: Track LLM generations specifically
with start_generation("text_generation", model="gpt-4") as span:
    response = llm.generate("Hello!")
    span.update(output=response)
```

## Configuration

The package uses environment variables for configuration:

- `Tracenet_TRACER`: The tracing backend to use (default: 'langfuse')
- `Tracenet_SERVICE_NAME`: Service name for framework integrations (default: 'agent_service')
- `AGENT_NAME`: Agent name for automatic tagging of all traces. Can be set programmatically or via environment variable (optional)

For Langfuse backend:
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST` (optional)

## API Reference

### Automatic Tracing

Just import the package and it will automatically:
- Detect and instrument supported frameworks
- Set up appropriate tracing backends
- Configure default settings

### Manual Instrumentation (Optional)

#### Decorators

`@trace(name=None, **kwargs)`
```python
@trace(name="custom_name", tags=["tag1", "tag2"])
def my_function():
    pass
```

#### Context Managers

`start_span(context, **kwargs)`
```python
with start_span("operation_name", tags=["tag1"]) as span:
    result = operation()
    span.update(output=result)
```

`start_generation(name, model, **kwargs)`
```python
with start_generation("text_gen", model="gpt-4") as span:
    response = llm.generate("prompt")
    span.update(output=response)
```

### Agent Name Configuration

`set_agent_name(name)`
```python
from tracenet import set_agent_name

# Set agent name for all traces (overrides AGENT_NAME environment variable)
set_agent_name('MyAgentName')
```

#### Environment Variable (Recommended)
```bash
# .env file
AGENT_NAME=MyProductionAgent
```

All traces will be automatically tagged with the agent name for better organization and filtering.

### Utility Functions

`flush()`
```python
from tracenet import flush

# After operations
flush()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 