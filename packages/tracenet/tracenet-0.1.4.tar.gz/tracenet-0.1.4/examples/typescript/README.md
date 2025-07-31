# Tracenet - TypeScript Examples

This directory contains TypeScript examples demonstrating how to use tracenet with OpenAI Agents using the `@stackgen-ai/tracenet` package.

## Features

- Zero-configuration tracing setup
- Automatic OpenAI Agents integration
- Manual span creation and management
- Integration with tracenet for observability

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- OpenAI API key
- Langfuse account

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy the example environment file:
```bash
cp env.example .env
```

3. Edit `.env` with your API keys:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Running the Example

```bash
npm start
```

The agent will generate a story about a robot discovering music, which will be traced automatically using the Tracenet package.

## Features Demonstrated

- **Auto-instrumentation**: Zero-config setup
- **OpenAI Agents Integration**: Automatic tracing of agent operations
- **Manual Spans**: Custom span creation and management
- **Error Handling**: Automatic error tracking
- **Automated Tracing**: All agent interactions are automatically traced using Tracenet

## Verification

1. Run the example and check the console output
2. Check that the Tracenet package is properly initialized by looking for console output indicating tracing setup
3. Visit your Langfuse dashboard to see the traces

## Additional Resources

- [Tracenet Documentation](https://github.com/stackgenhq/tracenet)
- [OpenAI Agents Documentation](https://platform.openai.com/docs/agents)
- [Langfuse Documentation](https://langfuse.com/docs) 