# Universal Auto-Tracing for Agentic Frameworks

Advanced tracing middleware for multiple agentic frameworks with **zero-configuration setup**. Just import and go - automatic agent lifecycle tracing with complete input/output capture for OpenAI Agents, LangChain, Vercel AI SDK, Anthropic, and more.

## ✨ Zero-Configuration Promise

```typescript
// 1. Set environment variables
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:3000  # optional

// 2. Import the package (auto-setup happens here!)
import '@stackgen-ai/tracenet';

// 3. Your existing code now works with full tracing! 🎉
import { Agent, run } from '@openai/agents';

const agent = new Agent({
  name: 'Assistant',
  instructions: 'You are a helpful assistant.'
});

const result = await run(agent, 'Hello!'); // Automatically traced!
```

This package automatically detects and instruments popular agentic frameworks without requiring any code changes.

## 🎯 Supported Frameworks

The middleware automatically detects and instruments the following frameworks:

### ✅ Currently Supported
- **@openai/agents** - OpenAI Agents SDK (native Langfuse integration)
- **openai** - OpenAI SDK (Langfuse observeOpenAI)
- **langchain** - LangChain framework (Langfuse native)
- **@vercel/ai** - Vercel AI SDK (OpenInference)
- **@anthropic-ai/sdk** - Anthropic SDK (OpenInference)
- **@google-cloud/aiplatform** - Google AI Platform (OpenInference)

### 🔄 Coming Soon
- **mistralai** - Mistral AI SDK
- **@aws-sdk/client-bedrock** - AWS Bedrock
- **groq-sdk** - Groq SDK
- **cohere-ai** - Cohere SDK

No configuration needed - just install the framework and import our middleware!

## 🎯 Architecture Goals

- **Backend Agnostic**: No vendor-specific code in your agent implementation
- **Auto + Manual**: Combines automatic instrumentation with manual tracing control
- **Zero Refactoring**: Switch tracing backends without changing agent code
- **Production Ready**: Leverages proven tracing technologies under the hood

## 🚀 Quick Start

### Installation

```bash
npm install @stackgen-ai/tracenet
```

### Zero-Config Setup (Recommended)

Just like the Python package, simply import and go! 

#### Step 1: Set Environment Variables

```bash
# .env file
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_BASEURL=https://cloud.langfuse.com  # Optional

# Agent Name for Automatic Tagging (optional)
AGENT_NAME=MyAgentName
```

#### Step 2: Import the Package (Auto-Setup!)

```typescript
// Just import the package - automatic setup happens here!
import '@stackgen-ai/tracenet';

// Your existing code now works with tracing automatically
import { Agent, Runner } from '@openai/agents';

const agent = new Agent({
  name: 'My Agent',
  instructions: 'You are a helpful assistant.',
  tools: [myTool]
});

const runner = new Runner();
const result = await runner.run(agent, 'Hello!'); // Automatically traced! 🎉
```

#### Step 3: Check Setup Status (Optional)

```typescript
import { getSetupStatus, isAutoInstrumentationActive } from '@stackgen-ai/tracenet';

const status = getSetupStatus();
console.log(status.instructions); // Shows if tracing is working

if (isAutoInstrumentationActive()) {
  console.log('🎯 Tracing is active! Your code is being automatically traced.');
}
```

### Manual Setup (If Needed)

If auto-setup doesn't work for your use case:

```typescript
import { initializeTracing, createSpan, TracingPresets } from '@stackgen-ai/tracenet';
import { Agent, Runner } from '@openai/agents';

// 1. Initialize tracing backend manually
await initializeTracing(TracingPresets.langfuseFromEnv());

// 2. Your agent code runs unchanged - auto-instrumentation works automatically
const agent = new Agent({
  name: 'My Agent',
  instructions: 'You are a helpful assistant.',
  tools: [myTool]
});

const runner = new Runner();
const result = await runner.run(agent, 'Hello!'); // Automatically traced!

// 3. Add manual spans for custom operations
const span = createSpan('custom_operation');
await span.trace(() => myCustomFunction());
```

## 🏷️ Agent Name Configuration

The middleware supports automatic agent name tagging to help organize and filter your traces:

### Option 1: Environment Variable (Recommended)

Set the `AGENT_NAME` environment variable and all traces will be automatically tagged:

```bash
# .env file
AGENT_NAME=MyProductionAgent
```

### Option 2: Programmatic Configuration

```typescript
import { setAgentName } from '@stackgen-ai/tracenet';

// Set agent name for all subsequent traces
setAgentName('MyDynamicAgent');

// All traces created after this will be tagged with 'MyDynamicAgent'
```

### Agent Name Benefits

- **Trace Organization**: Filter traces by agent in your Langfuse dashboard
- **Multi-Agent Systems**: Distinguish between different agents in complex workflows
- **Environment Separation**: Use different names for dev/staging/prod environments
- **Team Collaboration**: Identify which team member's agent generated specific traces

## 🏗️ Architecture Overview

### Backend Abstraction Layer

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Agent    │    │  tracenet  │    │ Tracing Backend │
│     Code        │───▶│   Middleware     │───▶│  (Langfuse,     │
│                 │    │                  │    │ OpenTelemetry)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Auto-Instrumentation Flow

The middleware leverages each backend's native auto-instrumentation:

- **Langfuse**: Uses `observeOpenAI()` for automatic OpenAI SDK tracing
- **OpenTelemetry**: Uses standard OTel auto-instrumentation libraries
- **Your Code**: Remains completely backend-agnostic

## 📋 Features

### ✅ Automatic Framework Detection

The package automatically detects and instruments supported frameworks when imported:

#### Currently Supported
- **@openai/agents** - OpenAI Agents SDK (auto-detected, highest priority)
- **openai** - OpenAI SDK standalone (auto-detected)
- **langchain** - LangChain framework (auto-detected)

#### Auto-Instrumentation Features
- **OpenAI SDK calls** (via Langfuse's `observeOpenAI` or OTel)
- **HTTP requests** (via OpenTelemetry HTTP instrumentation)
- **Database calls** (via OTel database instrumentations)
- **Framework-specific** (Next.js, Express, etc.)

#### Coming Soon
- **Vercel AI SDK** - Vercel AI framework
- **LlamaIndex** - LlamaIndex framework
- **More frameworks** - Let us know what you need!

### 🔧 Manual Instrumentation

Fine-grained control when you need it:

```typescript
// Span-based tracing
const span = createSpan('database_query', {
  table: 'users',
  operation: 'select'
});

await span.trace(async () => {
  const users = await db.users.findMany();
  span.addEvent('query_completed', { count: users.length });
  return users;
});

// Decorator-based tracing
class UserService {
  @traced('user_service.create_user')
  async createUser(userData: any) {
    // Method automatically traced
    return await this.db.users.create(userData);
  }
}

// Function wrapping
const tracedFunction = withTracing(
  myAsyncFunction,
  'my_operation',
  { component: 'user_module' }
);
```

### 🔄 Backend Switching

Switch backends without code changes:

```typescript
// Development: Use Langfuse (auto-load from env)
await initializeTracing(TracingPresets.langfuseFromEnv());

// Production: Switch to OpenTelemetry
await initializeTracing(TracingPresets.opentelemetry('my-service'));

// Your agent code remains exactly the same!
const result = await runner.run(agent, input);
```

## 🎛️ Supported Backends

### Environment Variables Setup

The middleware supports automatic configuration from environment variables, just like the official Langfuse SDKs:

```bash
# .env file
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_BASEURL=https://cloud.langfuse.com  # Optional, defaults to cloud.langfuse.com
```

### Langfuse Backend

```typescript
import { TracingPresets } from '@stackgen-ai/tracenet';

// Recommended: Auto-load from environment variables
await initializeTracing(TracingPresets.langfuseFromEnv());

// Alternative: Explicit credentials
await initializeTracing(TracingPresets.langfuse(
  'pk-lf-your-public-key',
  'sk-lf-your-secret-key',
  'https://cloud.langfuse.com' // optional
));
```

**Auto-instrumentation includes:**
- OpenAI SDK calls (GPT, embeddings, etc.)
- Agent tool executions
- LLM token usage and costs

### OpenTelemetry Backend

```typescript
await initializeTracing(TracingPresets.opentelemetry('my-service-name'));
```

**Auto-instrumentation includes:**
- HTTP/HTTPS requests
- Database queries (PostgreSQL, MongoDB, etc.)
- Redis operations
- AWS SDK calls
- And 50+ other libraries

### Custom Backends

Register your own tracing backend:

```typescript
import { registerTracingBackend, TracingBackend } from '@stackgen-ai/tracenet';

class MyCustomBackend implements TracingBackend {
  name = 'custom';
  
  async initialize(config: Record<string, any>): Promise<void> {
    // Initialize your tracing system
  }
  
  createSpan(context: SpanContext): Span {
    // Create and return a span
  }
  
  // ... implement other methods
}

registerTracingBackend('custom', () => new MyCustomBackend());

await initializeTracing({
  backend: 'custom',
  config: { /* your config */ }
});
```

## 🔍 Comprehensive Example

```typescript
import { 
  initializeTracing, 
  createSpan, 
  traced, 
  withTracing,
  TracingPresets,
  PerformanceTracer 
} from '@stackgen-ai/tracenet';

// Initialize tracing
await initializeTracing(TracingPresets.langfuse(publicKey, secretKey));

// External API call with manual tracing
async function fetchWeatherData(city: string) {
  const span = createSpan('external_api.weather_fetch', {
    api_provider: 'openweather',
    city: city
  });

  return await span.trace(async () => {
    const response = await fetch(`/weather?city=${city}`);
    span.addEvent('api_response_received', { 
      status: response.status 
    });
    return response.json();
  });
}

// Class with decorator-based tracing
class WeatherProcessor {
  @traced('weather_processing.validate')
  validateData(data: any): boolean {
    return data.temperature && data.conditions;
  }
}

// Tool with performance monitoring
const getWeather = tool({
  name: 'get_weather',
  execute: async ({ city }) => {
    // Performance timing
    PerformanceTracer.startTimer('weather_tool_execution');
    
    try {
      // Manual span for tool execution
      const toolSpan = createSpan('tool.get_weather', {
        tool_type: 'weather_lookup',
        city: city
      });

      return await toolSpan.trace(async () => {
        // Fetch data (traced automatically)
        const weatherData = await fetchWeatherData(city);
        
        // Process data (traced via decorator)
        const processor = new WeatherProcessor();
        const isValid = processor.validateData(weatherData);
        
        if (!isValid) {
          throw new Error('Invalid weather data');
        }

        return weatherData;
      });
    } finally {
      const duration = PerformanceTracer.endTimer('weather_tool_execution');
      console.log(`Tool execution: ${duration}ms`);
    }
  }
});

// Agent runs with full auto-instrumentation
const agent = new Agent({
  name: 'Weather Agent',
  tools: [getWeather]
});

const runner = new Runner();
const result = await runner.run(agent, "What's the weather in Tokyo?");

// Everything is automatically traced:
// - OpenAI SDK calls
// - Tool executions  
// - Manual spans
// - Performance metrics
// - External API calls
```

## 📊 Trace Hierarchy

The middleware creates a comprehensive trace hierarchy:

```
Session Span (manual)
├── Agent Execution (auto-instrumented)
│   ├── OpenAI API Call (auto via Langfuse/OTel)
│   ├── Tool Call: get_weather (auto)
│   │   ├── Tool Execution Span (manual)
│   │   ├── External API Call (manual)
│   │   └── Data Processing (decorator)
│   └── OpenAI API Call (auto)
└── Session Completion (manual)
```

## ⚙️ Configuration

### Full Configuration

```typescript
import { initializeTracing, TracingConfig } from '@stackgen-ai/tracenet';

const config: TracingConfig = {
  backend: 'langfuse',
  config: {
    publicKey: 'pk-lf-...',
    secretKey: 'sk-lf-...',
    baseUrl: 'https://cloud.langfuse.com'
  },
  enableAutoInstrumentation: true,  // Enable auto-instrumentation
  enableManualTracing: true,        // Enable manual spans
  serviceName: 'my-agent-service',
  environment: 'production',
  version: '1.0.0'
};

await initializeTracing(config);
```

### Environment Variables

```bash
# .env file
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

```typescript
// Automatic config from environment
await initializeTracing(TracingPresets.langfuse(
  process.env.LANGFUSE_PUBLIC_KEY!,
  process.env.LANGFUSE_SECRET_KEY!,
  process.env.LANGFUSE_HOST
));
```

## 🔧 Advanced Usage

### Custom Span Kinds

```typescript
import { createSpanWithKind } from '@stackgen-ai/tracenet';

// Different span types for different operations
const serverSpan = createSpanWithKind('http_request', 'server', {
  method: 'POST',
  endpoint: '/api/agents'
});

const clientSpan = createSpanWithKind('external_api_call', 'client', {
  service: 'openai',
  model: 'gpt-4'
});
```

### Performance Monitoring

```typescript
import { PerformanceTracer } from '@stackgen-ai/tracenet';

// Start timing
PerformanceTracer.startTimer('database_query', {
  query_type: 'SELECT',
  table: 'conversations'
});

// Perform operation
const conversations = await db.conversations.findMany();

// End timing (automatically captured in trace)
const duration = PerformanceTracer.endTimer('database_query');
```

### Conditional Tracing

```typescript
// Only trace in development/staging
if (process.env.NODE_ENV !== 'production') {
  await initializeTracing(TracingPresets.langfuse(publicKey, secretKey));
} else {
  // Use lightweight tracing in production
  await initializeTracing(TracingPresets.opentelemetry('prod-service'));
}
```

## 🧪 Testing

The middleware provides testing utilities:

```typescript
import { getCurrentBackend, createSpan } from '@stackgen-ai/tracenet';

// Mock tracing in tests
const mockBackend = {
  name: 'mock',
  initialize: async () => {},
  createSpan: () => mockSpan,
  flush: async () => {},
  shutdown: async () => {}
};

// Your tests run without actual tracing
```

## 🔄 Migration Guide

### From Direct Langfuse Usage

```typescript
// Before: Direct Langfuse
import { Langfuse } from 'langfuse';
const langfuse = new Langfuse({ ... });
const trace = langfuse.trace({ name: 'my-operation' });

// After: Backend-agnostic
import { initializeTracing, createSpan, TracingPresets } from '@stackgen-ai/tracenet';
await initializeTracing(TracingPresets.langfuse(publicKey, secretKey));
const span = createSpan('my-operation');
```

### From OpenTelemetry

```typescript
// Before: Direct OpenTelemetry
import { trace } from '@opentelemetry/api';
const tracer = trace.getTracer('my-service');
const span = tracer.startSpan('operation');

// After: Backend-agnostic
import { initializeTracing, createSpan, TracingPresets } from '@stackgen-ai/tracenet';
await initializeTracing(TracingPresets.opentelemetry('my-service'));
const span = createSpan('operation');
```

## 🎛️ API Reference

### Core Functions

- `initializeTracing(config)` - Initialize tracing backend
- `createSpan(name, attributes?)` - Create manual span
- `createSpanWithKind(name, kind, attributes?)` - Create span with specific kind
- `flushTraces()` - Flush pending traces
- `shutdownTracing()` - Shutdown tracing system

### Decorators & Utilities

- `@traced(name?, attributes?)` - Method decorator for tracing
- `withTracing(fn, name, attributes?)` - Function wrapper for tracing
- `PerformanceTracer.startTimer(name)` - Start performance timer
- `PerformanceTracer.endTimer(name)` - End performance timer

### Configuration

- `TracingPresets.langfuse(publicKey, secretKey, baseUrl?)` - Langfuse preset
- `TracingPresets.opentelemetry(serviceName?)` - OpenTelemetry preset
- `registerTracingBackend(name, factory)` - Register custom backend

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [Full docs](https://docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/tracenet/issues)
- **Discord**: [Community Discord](https://discord.gg/your-community)

---

**The middleware that makes tracing as easy as adding one line of initialization code.** 🚀 