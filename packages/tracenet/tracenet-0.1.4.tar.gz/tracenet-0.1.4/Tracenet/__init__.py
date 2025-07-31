"""
tracenet
=========

A universal tracing middleware for agent applications with support for multiple tracing backends.
Just import this package and it will automatically set up tracing.
"""

from .python.middleware import (
    trace,
    start_span,
    start_generation,
    flush,
    TracingBackend,
    SpanContext,
    get_tracer,
    _setup_native_integration,
    set_agent_name,
    set_session_id,
    get_session_id,
    clear_session_id
)

__version__ = "0.1.1"

# Automatically set up native integration when the package is imported
USING_NATIVE_INTEGRATION = _setup_native_integration()

__all__ = [
    'trace',
    'start_span',
    'start_generation',
    'flush',
    'TracingBackend',
    'SpanContext',
    'get_tracer',
    'set_agent_name',
    'set_session_id',
    'get_session_id',
    'clear_session_id'
] 