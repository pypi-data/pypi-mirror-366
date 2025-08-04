import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
from .logger import MongoLogger


def log_endpoint(logger: MongoLogger, **log_kwargs):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                await logger.log_custom("function_call", {
                    "function_name": func.__name__,
                    "success": True,
                    "response_time_ms": response_time,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    **log_kwargs
                })
                return result
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                await logger.log_custom("function_call", {
                    "function_name": func.__name__,
                    "success": False,
                    "error": str(e),
                    "response_time_ms": response_time,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    **log_kwargs
                })
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                asyncio.create_task(logger.log_custom("function_call", {
                    "function_name": func.__name__,
                    "success": True,
                    "response_time_ms": response_time,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    **log_kwargs
                }))
                return result
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                asyncio.create_task(logger.log_custom("function_call", {
                    "function_name": func.__name__,
                    "success": False,
                    "error": str(e),
                    "response_time_ms": response_time,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    **log_kwargs
                }))
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def log_function(logger: MongoLogger, event_type: str = "custom_event", **log_kwargs):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                await logger.log_custom(event_type, {
                    "function_name": func.__name__,
                    "success": True,
                    "response_time_ms": response_time,
                    **log_kwargs
                })
                return result
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                await logger.log_custom(event_type, {
                    "function_name": func.__name__,
                    "success": False,
                    "error": str(e),
                    "response_time_ms": response_time,
                    **log_kwargs
                })
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                asyncio.create_task(logger.log_custom(event_type, {
                    "function_name": func.__name__,
                    "success": True,
                    "response_time_ms": response_time,
                    **log_kwargs
                }))
                return result
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                asyncio.create_task(logger.log_custom(event_type, {
                    "function_name": func.__name__,
                    "success": False,
                    "error": str(e),
                    "response_time_ms": response_time,
                    **log_kwargs
                }))
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator