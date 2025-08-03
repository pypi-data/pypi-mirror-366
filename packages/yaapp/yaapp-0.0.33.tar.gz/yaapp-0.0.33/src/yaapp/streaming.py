"""
Streaming support for yaapp framework.

Provides SSE (Server-Sent Events) streaming capabilities with automatic detection
and manual streaming decorators.
"""

import asyncio
import inspect
import json
from typing import Any, AsyncGenerator, AsyncIterator, Callable, Generator, Iterator, Union
from functools import wraps

from .result import Result, Ok


def stream(func: Callable = None, *, format: str = "sse", buffer_size: int = 1024):
    """
    Decorator to mark a function for streaming output.
    
    Args:
        func: Function to decorate (when used as @stream)
        format: Streaming format ("sse", "json-lines", "raw")
        buffer_size: Buffer size for streaming
    
    Usage:
        @stream
        async def my_generator():
            for i in range(10):
                yield f"Item {i}"
        
        @stream(format="json-lines")
        def data_stream():
            for data in get_data():
                yield {"index": i, "data": data}
    """
    def decorator(f: Callable) -> Callable:
        f._yaapp_stream = True
        f._yaapp_stream_format = format
        f._yaapp_stream_buffer_size = buffer_size
        return f
    
    if func is None:
        # Used as @stream(format="json")
        return decorator
    else:
        # Used as @stream
        return decorator(func)


class StreamDetector:
    """Detects if a function should be exposed as a streaming endpoint."""
    
    @staticmethod
    def should_stream(func: Callable) -> bool:
        """Determine if function should automatically get SSE endpoint."""
        # 1. Explicit streaming decorator
        if hasattr(func, '_yaapp_stream') and func._yaapp_stream:
            return True
        
        # 2. Generator/AsyncGenerator functions
        if inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(func):
            return True
        
        # 3. Functions returning streaming types
        try:
            return_annotation = inspect.signature(func).return_annotation
            if hasattr(return_annotation, '__origin__'):
                origin = return_annotation.__origin__
                if origin in (AsyncIterator, Iterator, AsyncGenerator, Generator):
                    return True
            
            # Also check for typing._GenericAlias (Python 3.9+)
            import typing
            if hasattr(typing, 'get_origin') and hasattr(typing, 'get_args'):
                origin = typing.get_origin(return_annotation)
                if origin in (AsyncIterator, Iterator, AsyncGenerator, Generator):
                    return True
            
            # Check string representation as fallback
            annotation_str = str(return_annotation)
            if any(t in annotation_str for t in ['AsyncGenerator', 'AsyncIterator', 'Generator', 'Iterator']):
                return True
                
        except (AttributeError, TypeError):
            pass
        
        # 4. Functions with "stream" in name (heuristic)
        if '_stream' in func.__name__ or func.__name__.startswith('stream_'):
            return True
            
        return False
    
    @staticmethod
    def get_stream_format(func: Callable) -> str:
        """Get the streaming format for a function."""
        return getattr(func, '_yaapp_stream_format', 'sse')
    
    @staticmethod
    def get_buffer_size(func: Callable) -> int:
        """Get the buffer size for a function."""
        return getattr(func, '_yaapp_stream_buffer_size', 1024)


class StreamFormatter:
    """Formats streaming output for different protocols."""
    
    @staticmethod
    def format_sse(data: Any, event_type: str = "data") -> str:
        """Format data as Server-Sent Events."""
        if isinstance(data, dict):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        # Escape newlines for SSE format
        escaped_data = data_str.replace('\n', '\\n').replace('\r', '\\r')
        return f"event: {event_type}\ndata: {escaped_data}\n\n"
    
    @staticmethod
    def format_json_lines(data: Any) -> str:
        """Format data as JSON Lines (one JSON object per line)."""
        if isinstance(data, dict):
            return json.dumps(data) + '\n'
        else:
            return json.dumps({"data": data}) + '\n'
    
    @staticmethod
    def format_raw(data: Any) -> str:
        """Format data as raw text."""
        return str(data) + '\n'
    
    @classmethod
    def format_data(cls, data: Any, format_type: str = "sse", event_type: str = "data") -> str:
        """Format data according to specified format."""
        if format_type == "sse":
            return cls.format_sse(data, event_type)
        elif format_type == "json-lines":
            return cls.format_json_lines(data)
        elif format_type == "raw":
            return cls.format_raw(data)
        else:
            # Default to SSE
            return cls.format_sse(data, event_type)


class StreamExecutor:
    """Executes streaming functions with proper async handling."""
    
    @staticmethod
    async def execute_stream(func: Callable, kwargs: dict) -> AsyncGenerator[str, None]:
        """
        Execute a streaming function and yield formatted output.
        
        Args:
            func: Function to execute (can be sync/async generator or regular function)
            kwargs: Arguments to pass to function
            
        Yields:
            Formatted streaming data
        """
        format_type = StreamDetector.get_stream_format(func)
        formatter = StreamFormatter()
        
        try:
            # Handle different function types
            if inspect.isasyncgenfunction(func):
                # Async generator function
                async for item in func(**kwargs):
                    yield formatter.format_data(item, format_type)
            
            elif inspect.isgeneratorfunction(func):
                # Sync generator function - run in thread pool
                gen = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: func(**kwargs)
                )
                for item in gen:
                    yield formatter.format_data(item, format_type)
            
            elif asyncio.iscoroutinefunction(func):
                # Async function - check if it returns an async iterator
                result = await func(**kwargs)
                if hasattr(result, '__aiter__'):
                    async for item in result:
                        yield formatter.format_data(item, format_type)
                else:
                    # Single async result
                    yield formatter.format_data(result, format_type)
            
            else:
                # Sync function - run in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: func(**kwargs)
                )
                
                if hasattr(result, '__iter__') and not isinstance(result, (str, bytes, dict)):
                    # Iterable result
                    for item in result:
                        yield formatter.format_data(item, format_type)
                else:
                    # Single result
                    yield formatter.format_data(result, format_type)
                    
        except Exception as e:
            # Send error as stream event
            error_data = {"error": str(e), "type": "execution_error"}
            yield formatter.format_data(error_data, format_type, "error")


class StreamingCapableMixin:
    """Mixin to add streaming capabilities to exposers."""
    
    def is_streaming_function(self, func: Callable) -> bool:
        """Check if function should be exposed as streaming."""
        return StreamDetector.should_stream(func)
    
    async def execute_streaming(self, func: Callable, kwargs: dict) -> AsyncGenerator[str, None]:
        """Execute function as stream."""
        async for chunk in StreamExecutor.execute_stream(func, kwargs):
            yield chunk


# Utility functions for common streaming patterns

async def stream_json_array(items, chunk_size: int = 10):
    """
    Stream an array of items as JSON chunks.
    
    Args:
        items: Iterable of items to stream
        chunk_size: Number of items per chunk
    """
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield {"chunk": chunk, "partial": True}
            chunk = []
    
    if chunk:
        yield {"chunk": chunk, "partial": False}


async def stream_file_lines(file_path: str, encoding: str = 'utf-8'):
    """
    Stream file contents line by line.
    
    Args:
        file_path: Path to file to stream
        encoding: File encoding
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            line_number = 1
            for line in f:
                yield {
                    "line_number": line_number,
                    "content": line.rstrip('\n\r'),
                    "timestamp": asyncio.get_event_loop().time()
                }
                line_number += 1
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.001)
    except Exception as e:
        yield {"error": str(e), "type": "file_error"}


async def stream_progress(total: int, label: str = "Progress"):
    """
    Stream progress updates.
    
    Args:
        total: Total number of items
        label: Progress label
    """
    for i in range(total + 1):
        percentage = (i / total) * 100 if total > 0 else 100
        yield {
            "progress": {
                "current": i,
                "total": total,
                "percentage": round(percentage, 2),
                "label": label
            }
        }
        await asyncio.sleep(0.1)  # Simulate work


# Example streaming functions

@stream
async def example_counter(start: int = 0, end: int = 10, delay: float = 1.0):
    """Example streaming function that counts from start to end."""
    for i in range(start, end + 1):
        yield {"count": i, "timestamp": asyncio.get_event_loop().time()}
        await asyncio.sleep(delay)


@stream(format="json-lines")
async def example_data_feed(count: int = 5):
    """Example data feed streaming function."""
    import time
    for i in range(count):
        yield {
            "id": i,
            "data": f"Data item {i}",
            "timestamp": time.time(),
            "metadata": {"sequence": i, "total": count}
        }
        await asyncio.sleep(0.5)


def example_file_processor(file_path: str):
    """Example sync generator for file processing."""
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                yield {
                    "line": line_num,
                    "length": len(line),
                    "content": line.strip()
                }
    except Exception as e:
        yield {"error": str(e)}