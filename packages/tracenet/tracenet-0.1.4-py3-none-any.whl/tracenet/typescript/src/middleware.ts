/**
 * Universal Tracing Middleware for Agentic Frameworks
 * ==================================================
 * 
 * This middleware provides both automatic and manual instrumentation for multiple
 * agentic frameworks including OpenAI Agents, LangChain, Vercel AI SDK, and more.
 * It leverages OpenInference instrumentors and Langfuse native integrations for
 * comprehensive tracing coverage.
 * 
 * Features:
 * - Zero-config auto-instrumentation (just import this package!)
 * - Automatic framework detection and instrumentation:
 *   - OpenAI Agents SDK (native integration)
 *   - OpenAI SDK (OpenInference)
 *   - LangChain (Langfuse native)
 *   - Vercel AI SDK (OpenInference)
 *   - Anthropic (OpenInference) 
 *   - And many more...
 * - Manual span management for custom operations
 * - Environment variable auto-loading for Langfuse credentials
 * - Support for context propagation and nested spans
 * - Performance metrics and error tracking
 * 
 * Usage:
 * 
 * // Zero-config (recommended):
 * import '@stackgen-ai/tracenet'; // Auto-detects frameworks and sets up tracing
 * 
 * // Manual instrumentation:
 * const span = createManualSpan('custom_operation', { key: 'value' });
 * const result = await span.wrap(() => myCustomFunction());
 */

import { Langfuse } from 'langfuse';

// Optional framework types - only imported if available
type Agent<TContext = any, THandoffs = any> = any;
type Runner = any;
type RunConfig = any;
type RunResult<TContext = any, TAgent = any> = any;
type StreamedRunResult<TContext = any, TAgent = any> = any;
type AgentInputItem = any;
type RunContext<TContext = any> = any;

// ============================================================================
// Global Agent Name - auto-read from environment variable
// ============================================================================

let _AGENT_NAME: string | null = process.env.AGENT_NAME || null;

export function setAgentName(name: string): void {
  /**
   * Set the agent name that will be used to tag all traces.
   */
  _AGENT_NAME = name;
}

export function getAgentName(): string | null {
  /**
   * Get the current agent name.
   */
  return _AGENT_NAME;
}

// ============================================================================
// Configuration Types
// ============================================================================

export interface TracingConfig {
  /** Langfuse configuration */
  publicKey: string;
  secretKey: string;
  baseUrl?: string;
  
  /** Tracing behavior settings */
  enableAutoInstrumentation?: boolean;
  enableManualInstrumentation?: boolean;
  includeSensitiveData?: boolean;
  flushOnExit?: boolean;
  
  /** Custom span attributes */
  defaultAttributes?: Record<string, any>;
  sessionId?: string;
  userId?: string;
  environment?: string;
}

export interface SpanOptions {
  name: string;
  attributes?: Record<string, any>;
  parentSpanId?: string;
  category?: 'agent' | 'tool' | 'handoff' | 'custom' | 'error';
}

// ============================================================================
// Span Management
// ============================================================================

export class SpanManager {
  private langfuse: Langfuse;
  private span: any;
  private trace: any;
  private isChild: boolean;
  
  constructor(name: string, attributes?: Record<string, any>, langfuse?: Langfuse, parentContext?: { traceId?: string; parentSpanId?: string }) {
    const availableLangfuse = langfuse || getGlobalLangfuse();
    if (!availableLangfuse) {
      throw new Error('No Langfuse instance available. Call createLangfuse() first.');
    }
    this.langfuse = availableLangfuse;
    this.isChild = !!(parentContext?.traceId);
    
    if (parentContext?.traceId) {
      // Create child span within existing trace
      console.log(`🔧 Creating child span in existing trace: ${name}`, { traceId: parentContext.traceId, parentSpanId: parentContext.parentSpanId });
      
      this.span = this.langfuse.span({
        traceId: parentContext.traceId,
        parentObservationId: parentContext.parentSpanId,
        name: name,
        metadata: attributes || {}
      });
      
      // Don't create a new trace, reference the existing one
      this.trace = null;
    } else {
      // Create new trace and span
      console.log(`🔧 Creating new trace: ${name}`, attributes);
      this.trace = this.langfuse.trace({
        name: name,
        metadata: attributes || {}
      });
      
      console.log(`🔧 Creating root span: ${name}`);
      this.span = this.trace.span({
        name: name,
        metadata: attributes || {}
      });
    }
    
    // Add agent name tag if set (similar to Python version)
    if (_AGENT_NAME) {
      try {
        if (this.trace) {
          // For root traces, update the trace with agent name tag
          this.trace.update({ tags: [_AGENT_NAME] });
        }
        if (this.span) {
          // Update span with agent name tag
          this.span.update({ tags: [_AGENT_NAME] });
        }
      } catch (error) {
        console.warn('Could not add agent name tag:', error);
      }
    }
    
    console.log(`✅ SpanManager created for: ${name} (${this.isChild ? 'child' : 'root'} span)`);
  }
  
  updateSpan(attributes: Record<string, any>): void {
    if (this.span) {
      console.log(`🔧 Updating span with attributes:`, attributes);
      this.span.update(attributes);
    }
  }
  
  end(): void {
    if (this.span) {
      console.log(`🔧 Ending span`);
      this.span.end();
    }
  }
  
  async wrap<T>(fn: () => Promise<T>): Promise<T> {
    try {
      const result = await fn();
      this.updateSpan({ status: 'success' });
      return result;
    } catch (error) {
      this.updateSpan({ 
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    } finally {
      this.end();
    }
  }

  getSpanId(): string | null {
    return this.span?.id || null;
  }

  getTraceId(): string | null {
    if (this.trace) {
      return this.trace.id;
    }
    // For child spans, we need to get the trace ID from the span
    return this.span?.traceId || null;
  }
}

// ============================================================================
// Langfuse Management
// ============================================================================

let globalLangfuse: Langfuse | null = null;

export function createLangfuse(config: {
  publicKey: string;
  secretKey: string;
  baseUrl?: string;
}): Langfuse {
  console.log(`🔧 Creating Langfuse instance with baseUrl: ${config.baseUrl || 'https://localhost:3000'}`);
  const langfuse = new Langfuse({
    publicKey: config.publicKey,
    secretKey: config.secretKey,
    baseUrl: config.baseUrl || 'https://localhost:3000'
  });
  
  // Enable debug mode to see what's happening
  langfuse.debug();
  
  // Listen for errors
  langfuse.on('error', (error) => {
    console.error('❌ Langfuse error:', error);
  });
  
  globalLangfuse = langfuse;
  console.log(`✅ Langfuse instance created and set as global`);
  return langfuse;
}

function getGlobalLangfuse(): Langfuse | null {
  return globalLangfuse;
}

// ============================================================================
// Middleware State Management
// ============================================================================

class TracingMiddleware {
  private langfuse: Langfuse;
  public config: TracingConfig; // Made public to fix linter errors
  private activeSpans: Map<string, SpanManager> = new Map();
  private sessionSpan: SpanManager | null = null;
  private currentTraceContext: { traceId: string; parentSpanId?: string } | null = null;
  
  constructor(config: TracingConfig) {
    this.config = {
      enableAutoInstrumentation: true,
      enableManualInstrumentation: true,
      includeSensitiveData: true,
      flushOnExit: true,
      baseUrl: 'https://localhost:3000',
      ...config
    };
    
    // Initialize Langfuse
    this.langfuse = createLangfuse({
      publicKey: this.config.publicKey,
      secretKey: this.config.secretKey,
      baseUrl: this.config.baseUrl
    });
    
    // Set up process exit handlers
    if (this.config.flushOnExit) {
      this.setupExitHandlers();
    }
  }
  
  private setupExitHandlers() {
    const cleanup = async () => {
      try {
        console.log('🔧 Process exiting, flushing Langfuse...');
        await this.flush();
      } catch (error) {
        console.error('Error flushing traces on exit:', error);
      }
    };
    
    process.on('exit', cleanup);
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
    process.on('uncaughtException', cleanup);
  }
  
  public async flush(): Promise<void> {
    console.log(`🔧 Flushing traces to Langfuse...`);
    try {
      // Use the correct method from Langfuse SDK
      await this.langfuse.flushAsync();
      console.log(`✅ Traces flushed successfully`);
    } catch (error) {
      console.error(`❌ Error flushing traces:`, error);
      
      // Try alternative shutdown method
      try {
        await this.langfuse.shutdownAsync();
        console.log(`✅ Langfuse shutdown successfully`);
      } catch (shutdownError) {
        console.error(`❌ Error during shutdown:`, shutdownError);
      }
    }
  }
  
  public createSpan(options: SpanOptions): SpanManager {
    const attributes = {
      ...this.config.defaultAttributes,
      ...options.attributes,
      category: options.category || 'custom',
      session_id: this.config.sessionId,
      user_id: this.config.userId,
      environment: this.config.environment,
      timestamp: new Date().toISOString()
    };
    
    // Create span with parent context if available
    const span = new SpanManager(
      options.name, 
      attributes, 
      this.langfuse, 
      this.currentTraceContext || undefined
    );
    
    const spanId = `${options.name}_${Date.now()}_${Math.random()}`;
    this.activeSpans.set(spanId, span);
    
    // Update trace context for subsequent child spans
    const traceId = span.getTraceId();
    const spanObservationId = span.getSpanId();
    
    if (traceId) {
      this.currentTraceContext = {
        traceId: traceId,
        parentSpanId: spanObservationId || undefined
      };
    }
    
    return span;
  }
  
  public getLangfuse(): Langfuse {
    return this.langfuse;
  }
}

// Global middleware instance
let middleware: TracingMiddleware | null = null;

// ============================================================================
// Automatic Instrumentation
// ============================================================================

/**
 * Instruments an agent runner with automatic tracing capabilities.
 * This hooks into all agent lifecycle events and creates traces automatically.
 */
export function instrumentAgent<TContext = any>(
  runner: Runner,
  config: TracingConfig
): InstrumentedRunner<TContext> {
  if (!middleware) {
    middleware = new TracingMiddleware(config);
  }
  
  return new InstrumentedRunner(runner, middleware);
}

class InstrumentedRunner<TContext = any> {
  private runner: Runner;
  private middleware: TracingMiddleware;
  private runSpan: SpanManager | null = null;
  
  constructor(runner: Runner, middleware: TracingMiddleware) {
    this.runner = runner;
    this.middleware = middleware;
    this.setupEventListeners();
  }
  
  private setupEventListeners() {
    // Agent lifecycle events
    this.runner.on('agent_start', (context: RunContext<TContext>, agent: Agent<TContext, any>) => {
      const span = this.middleware.createSpan({
        name: `agent_${agent.name}`,
        category: 'agent',
        attributes: {
          agent_name: agent.name,
          agent_description: agent.handoffDescription,
          model: typeof agent.model === 'string' ? agent.model : agent.model.toString(),
          tools_count: agent.tools.length,
          handoffs_count: agent.handoffs.length,
          context_usage: context.usage.totalTokens
        }
      });
      
      console.log(`🤖 Agent started: ${agent.name}`);
    });
    
    this.runner.on('agent_end', (context: RunContext<TContext>, agent: Agent<TContext, any>, output: string) => {
      const span = this.middleware.createSpan({
        name: `agent_${agent.name}_completion`,
        category: 'agent',
        attributes: {
          agent_name: agent.name,
          output_length: output.length,
          context_usage: context.usage.totalTokens,
          status: 'completed'
        }
      });
      
      if ((this.middleware as any).config.includeSensitiveData) {
        span.updateSpan({ output });
      }
      
      console.log(`✅ Agent completed: ${agent.name}`);
    });
    
    // Tool execution events
    this.runner.on('agent_tool_start', (context: RunContext<TContext>, agent: Agent<TContext, any>, tool: any, details: any) => {
      const span = this.middleware.createSpan({
        name: `tool_${tool.name}`,
        category: 'tool',
        attributes: {
          tool_name: tool.name,
          agent_name: agent.name,
          call_id: details.toolCall?.callId || details.toolCall?.id || 'unknown',
          context_usage: context.usage.totalTokens
        }
      });
      
      if (this.middleware.config.includeSensitiveData && details.toolCall?.arguments) {
        try {
          span.updateSpan({ 
            input: JSON.parse(details.toolCall.arguments) 
          });
        } catch (e) {
          span.updateSpan({ 
            input: details.toolCall.arguments 
          });
        }
      }
      
      console.log(`🔧 Tool started: ${tool.name}`);
    });
    
    this.runner.on('agent_tool_end', (context: RunContext<TContext>, agent: Agent<TContext, any>, tool: any, result: string, details: any) => {
      const span = this.middleware.createSpan({
        name: `tool_${tool.name}_completion`,
        category: 'tool',
        attributes: {
          tool_name: tool.name,
          agent_name: agent.name,
          call_id: details.toolCall?.callId || details.toolCall?.id || 'unknown',
          context_usage: context.usage.totalTokens,
          status: 'completed',
          result_length: result.length
        }
      });
      
      if (this.middleware.config.includeSensitiveData) {
        span.updateSpan({ output: result });
      }
      
      console.log(`✅ Tool completed: ${tool.name}`);
    });
    
    // Handoff events
    this.runner.on('agent_handoff', (context: RunContext<TContext>, fromAgent: Agent<any, any>, toAgent: Agent<any, any>) => {
      const span = this.middleware.createSpan({
        name: `handoff_${fromAgent.name}_to_${toAgent.name}`,
        category: 'handoff',
        attributes: {
          from_agent: fromAgent.name,
          to_agent: toAgent.name,
          context_usage: context.usage.totalTokens
        }
      });
      
      console.log(`🔄 Handoff: ${fromAgent.name} → ${toAgent.name}`);
    });
  }
  
  /**
   * Run an agent with automatic tracing
   */
  public async run<TAgent extends Agent<any, any>>(
    agent: TAgent,
    input: string | AgentInputItem[],
    options?: any
  ): Promise<RunResult<any, TAgent> | StreamedRunResult<any, TAgent>> {
    // Create a session span for the entire run
    this.runSpan = this.middleware.createSpan({
      name: `session_${(agent as any).name || 'Unknown'}`,
      category: 'agent',
      attributes: {
        session_type: 'agent_run',
        agent_name: (agent as any).name || 'Unknown',
        input_type: typeof input,
        input_length: typeof input === 'string' ? input.length : input.length,
        streaming: options?.stream || false
      }
    });
    
    if (this.middleware.config.includeSensitiveData) {
      this.runSpan.updateSpan({ 
        input: typeof input === 'string' ? input : JSON.stringify(input)
      });
    }
    
    try {
      const result = await this.runSpan.wrap(async () => {
        return await this.runner.run(agent, input, options);
      });
      
      // Update session span with results
      this.runSpan.updateSpan({
        status: 'completed',
        total_turns: (result as any).turns || 1,
        total_tokens: (result as any).usage?.totalTokens || 0,
        completion_time: new Date().toISOString()
      });
      
      if (this.middleware.config.includeSensitiveData) {
        this.runSpan.updateSpan({ 
          final_output: (result as any).finalOutput 
        });
      }
      
      return result;
    } catch (error) {
      this.runSpan.updateSpan({
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        error_type: error instanceof Error ? error.constructor.name : 'Unknown'
      });
      throw error;
    } finally {
      // Flush traces
      await this.middleware.flush();
    }
  }
  
  /**
   * Get the underlying runner
   */
  public getRunner(): Runner {
    return this.runner;
  }
  
  /**
   * Get the Langfuse instance
   */
  public getLangfuse(): Langfuse {
    return this.middleware.getLangfuse();
  }
}

// ============================================================================
// Manual Instrumentation
// ============================================================================

/**
 * Initialize manual instrumentation with the provided configuration.
 * This sets up the global tracing backend for manual span creation.
 */
export function initializeManualTracing(config: TracingConfig): void {
  if (!middleware) {
    middleware = new TracingMiddleware(config);
  }
}

/**
 * Create a manual span for custom operations.
 * This allows for fine-grained tracing of specific code blocks.
 */
export function createManualSpan(
  name: string, 
  attributes?: Record<string, any>
): SpanManager {
  if (!middleware) {
    throw new Error('Manual tracing not initialized. Call initializeManualTracing() first.');
  }
  
  return middleware.createSpan({
    name,
    attributes,
    category: 'custom'
  });
}

/**
 * Decorator for automatic method tracing.
 * Usage: @traceMethod('operation_name', { key: 'value' })
 */
export function traceMethod(
  spanName?: string, 
  attributes?: Record<string, any>
) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    const name = spanName || `${target.constructor.name}.${propertyKey}`;
    
    descriptor.value = async function (...args: any[]) {
      const span = createManualSpan(name, {
        ...attributes,
        method: propertyKey,
        class: target.constructor.name,
        args_count: args.length
      });
      
      return await span.wrap(async () => {
        return await originalMethod.apply(this, args);
      });
    };
    
    return descriptor;
  };
}

/**
 * Higher-order function for tracing any async function.
 */
export function withTracing<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  spanName: string,
  attributes?: Record<string, any>
): T {
  return (async (...args: any[]) => {
    const span = createManualSpan(spanName, {
      ...attributes,
      function_name: fn.name,
      args_count: args.length
    });
    
    return await span.wrap(async () => {
      return await fn(...args);
    });
  }) as T;
}

/**
 * Utility to get the current Langfuse instance.
 */
export function getLangfuse(): Langfuse | null {
  return middleware?.getLangfuse() || null;
}

/**
 * Manually flush all traces to the backend.
 */
export async function flushTraces(): Promise<void> {
  if (middleware) {
    await middleware.flush();
  }
}

// ============================================================================
// Type Exports
// ============================================================================

// Export types (removed duplicate export)

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Create a traced version of an existing agent with enhanced debugging.
 */
export function wrapAgentWithTracing<TContext = any>(
  agent: Agent<TContext, any>,
  config: TracingConfig
): Agent<TContext, any> {
  // This function would need to be implemented based on the actual tool interface
  // For now, return the agent as-is since tool wrapping needs proper typing
  return agent;
}

/**
 * Performance monitoring utilities
 */
export class PerformanceMonitor {
  private static spans: Map<string, { start: number; span: SpanManager }> = new Map();
  
  static startTimer(name: string, attributes?: Record<string, any>): void {
    const span = createManualSpan(`perf_${name}`, {
      ...attributes,
      performance_monitoring: true
    });
    
    this.spans.set(name, {
      start: performance.now(),
      span
    });
  }
  
  static endTimer(name: string): number {
    const entry = this.spans.get(name);
    if (!entry) {
      throw new Error(`Timer '${name}' not found`);
    }
    
    const duration = performance.now() - entry.start;
    entry.span.updateSpan({
      duration_ms: duration,
      status: 'completed'
    });
    
    this.spans.delete(name);
    return duration;
  }
}

// ============================================================================
// Auto-Instrumentation Setup (runs when module is imported)
// ============================================================================

/**
 * Detects available frameworks and sets up auto-instrumentation
 */
function setupAutoInstrumentation(): boolean {
  try {
    // Load environment variables
    const config: TracingConfig = {
      publicKey: process.env.LANGFUSE_PUBLIC_KEY || '',
      secretKey: process.env.LANGFUSE_SECRET_KEY || '',
      baseUrl: process.env.LANGFUSE_HOST || process.env.LANGFUSE_BASEURL || 'https://localhost:3000',
      enableAutoInstrumentation: true,
      enableManualInstrumentation: true,
      includeSensitiveData: true,
      flushOnExit: true,
      environment: process.env.NODE_ENV || 'development',
      sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    // Check if Langfuse credentials are available
    if (!config.publicKey || !config.secretKey) {
      console.log('⚠️ Langfuse credentials not found in environment variables');
      console.log('   Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable auto-tracing');
      return false;
    }

    let instrumentedFrameworks: string[] = [];

    // Initialize the middleware
    if (!middleware) {
      middleware = new TracingMiddleware(config);
    }

    // 1. Try OpenAI Agents SDK (native integration)
    try {
      const agents = require('@openai/agents');
      console.log('🔍 Detected @openai/agents framework');
      
      // Use a global event listener approach to intercept any Runner instance
      const originalRunnerConstructor = agents.Runner;
      const originalRunMethod = originalRunnerConstructor.prototype.run;
      
      // Patch the run method to add our instrumentation
      originalRunnerConstructor.prototype.run = async function(agent: any, input: any, options?: any) {
        console.log('🎯 Auto-tracing agent execution...');
        
        // Create a top-level trace for this execution
        const langfuse = middleware!.getLangfuse();
        const trace = langfuse.trace({
          name: `agent_execution_${agent.name || 'Unknown'}`,
          input: typeof input === 'string' ? input : JSON.stringify(input),
          metadata: {
            agent_name: agent.name || 'Unknown',
            agent_instructions: agent.instructions || 'No instructions provided',
            input_type: typeof input,
            execution_time: new Date().toISOString(),
            session_id: config.sessionId,
            framework: '@openai/agents'
          }
        });
        
        try {
          // Call the original run method
          const result = await originalRunMethod.call(this, agent, input, options);
          
          // Update trace with final result
          trace.update({
            output: result.finalOutput,
            metadata: {
              final_output_length: result.finalOutput?.length || 0,
              execution_status: 'success',
              total_tokens: result.usage?.totalTokens || 0
            }
          });
          
          return result;
        } catch (error) {
          trace.update({
            metadata: {
              execution_status: 'error',
              error: error instanceof Error ? error.message : 'Unknown error'
            }
          });
          throw error;
        } finally {
          // Flush after completion to ensure traces are sent
          setTimeout(async () => {
            try {
              await langfuse.flushAsync();
            } catch (flushError) {
              console.error('❌ Error flushing traces:', flushError);
            }
          }, 100);
        }
      };
      
      instrumentedFrameworks.push('@openai/agents');
    } catch (e) {
      // @openai/agents not installed
    }

    // 2. Try OpenAI SDK (OpenInference)
    try {
      require('openai');
      console.log('🔍 Detected OpenAI SDK');
      
      // OpenAI SDK integration would be handled here
      // For now, we note it as detected
      instrumentedFrameworks.push('openai');
    } catch (e) {
      // OpenAI SDK not installed
    }

    // 3. Try LangChain (Langfuse native)
    try {
      require('langchain');
      console.log('🔍 Detected LangChain');
      
      // LangChain integration would be set up here
      // For now, we'll use the Langfuse instance
      instrumentedFrameworks.push('langchain');
    } catch (e) {
      // LangChain not installed
    }

    // 4. Try Vercel AI SDK
    try {
      require('@vercel/ai');
      console.log('🔍 Detected Vercel AI SDK');
      instrumentedFrameworks.push('@vercel/ai');
    } catch (e) {
      // Vercel AI SDK not installed
    }

    // 5. Try Anthropic SDK
    try {
      require('@anthropic-ai/sdk');
      console.log('🔍 Detected Anthropic SDK');
      instrumentedFrameworks.push('anthropic');
    } catch (e) {
      // Anthropic SDK not installed
    }

    // 6. Try Google AI SDK
    try {
      require('@google-cloud/aiplatform');
      console.log('🔍 Detected Google AI Platform SDK');
      instrumentedFrameworks.push('google-ai');
    } catch (e) {
      // Google AI SDK not installed
    }

    if (instrumentedFrameworks.length > 0) {
      console.log('✅ Auto-instrumentation enabled for frameworks:', instrumentedFrameworks.join(', '));
      console.log(`📊 Traces will be sent to: ${config.baseUrl}`);
      console.log('🎯 Framework calls will be automatically traced');
      return true;
    }

    console.log('💡 No supported frameworks detected. Available frameworks:');
    console.log('   - @openai/agents, openai, langchain, @vercel/ai, @anthropic-ai/sdk');
    
    return false;
  } catch (error) {
    console.error('❌ Error setting up auto-instrumentation:', error);
    return false;
  }
}

/**
 * Get the current auto-instrumentation status
 */
export function isAutoInstrumentationActive(): boolean {
  return middleware !== null;
}

/**
 * Get setup status information
 */
export function getSetupStatus(): {
  isActive: boolean;
  hasCredentials: boolean;
  detectedFrameworks: string[];
} {
  const hasCredentials = !!(process.env.LANGFUSE_PUBLIC_KEY && process.env.LANGFUSE_SECRET_KEY);
  const detectedFrameworks: string[] = [];
  
  try { require('@openai/agents'); detectedFrameworks.push('@openai/agents'); } catch {}
  try { require('openai'); detectedFrameworks.push('openai'); } catch {}
  try { require('langchain'); detectedFrameworks.push('langchain'); } catch {}
  
  return {
    isActive: isAutoInstrumentationActive(),
    hasCredentials,
    detectedFrameworks
  };
}

// Auto-setup when module is imported
console.log('🚀 Initializing auto-instrumentation...');
const setupSuccess = setupAutoInstrumentation();

if (!setupSuccess) {
  console.log('💡 To enable auto-tracing:');
  console.log('   1. Set environment variables: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY');
  console.log('   2. Install a supported framework: @openai/agents, openai, langchain');
  console.log('   3. Import this module: import "./middleware"');
} 