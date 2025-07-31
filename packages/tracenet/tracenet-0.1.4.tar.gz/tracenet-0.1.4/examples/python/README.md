# Python Examples for tracenet

This directory contains Python examples demonstrating how to use the `tracenet` package for comprehensive tracing and observability of AI agents and language model applications.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Langfuse instance (local or cloud)

### Installation

1. Clone the repository and navigate to the examples directory:
```bash
git clone https://github.com/stackgenhq/tracenet
cd tracenet/examples/python
```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys and configuration
   ```

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Langfuse Configuration for Observability
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=http://localhost:3000

# Agent Configuration
AGENT_NAME=creative_story_agent
tracenet_TRACER=langfuse
```

## Running the Examples

### Hello World Example

A simple example demonstrating basic tracing functionality:

```bash
python hello-world.py
```

This will:
1. Initialize the tracing system
2. Create a simple agent that generates a creative story
3. Demonstrate automatic and manual tracing
4. Show how to use spans and custom attributes

### Code Structure

The example demonstrates several key concepts:

1. **Automatic Framework Detection**
```python
import tracenet```

2. **Manual Tracing**
```python
from tracenet import trace, start_span, set_agent_name

@trace(name="generate_story")
def generate_story(prompt):
    with start_span("story_generation") as span:
        # Your code here
        span.update(output=result)
```

3. **Agent Configuration**
```python
# Set via environment variable
AGENT_NAME=creative_story_agent

# Or programmatically
from tracenet import set_agent_name
set_agent_name('creative_story_agent')
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `tracenet_TRACER` | Tracing backend to use | `langfuse` |
| `tracenet_SERVICE_NAME` | Service name for traces | `agent_service` |
| `AGENT_NAME` | Agent identifier for grouping traces | None |

## Best Practices

1. **Agent Names**: Always set an agent name either via environment variable or programmatically:
```python
from tracenet import set_agent_name
set_agent_name('my_agent_name')
```

2. **Error Handling**: The middleware automatically handles errors and updates spans appropriately.

3. **Cleanup**: For long-running applications, flush traces periodically:
```python
from tracenet import flush
flush()
```

## Troubleshooting

1. **Import Error**: `ModuleNotFoundError: No module named 'tracenet'`
   
   Solution: Install the package:
   ```bash
   pip install tracenet
   ```

2. **No Traces Appearing**: Check that your Langfuse API keys are correct and the host is accessible.

3. **Missing Agent Name**: Set the agent name via environment variable or programmatically.

## Additional Resources

- [tracenet Documentation](https://github.com/stackgenhq/tracenet)
- [Langfuse Documentation](https://langfuse.com/docs) 