from prometheus_client import Counter, Histogram
import time
import asyncio

class APIMetrics:
    """Centralized class for managing API metrics"""

    # Request counter
    REQUEST_COUNTER = Counter(
        'api_requests_total', 
        'Total number of API requests', 
        ['method', 'endpoint', 'status']
    )

    # Response time histogram
    RESPONSE_TIME = Histogram(
        'api_response_time_seconds', 
        'Response time of API endpoints', 
        ['method', 'endpoint']
    )

    # Error counter
    ERROR_COUNTER = Counter(
        'api_errors_total', 
        'Total number of API errors', 
        ['method', 'endpoint', 'error_type']
    )

    # Execution time tracking for specific methods
    METHOD_EXECUTION_TIME = Histogram(
        'method_execution_time_seconds', 
        'Execution time of specific methods', 
        ['method_name']
    )

def track_method_performance(method_name):
    """Decorator to track execution time of specific methods"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                APIMetrics.METHOD_EXECUTION_TIME.labels(method_name=method_name).observe(execution_time)
                return result
            except Exception as e:
                APIMetrics.ERROR_COUNTER.labels(method=func.__name__, endpoint=method_name, error_type=type(e).__name__).inc()
                raise

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                APIMetrics.METHOD_EXECUTION_TIME.labels(method_name=method_name).observe(execution_time)
                return result
            except Exception as e:
                APIMetrics.ERROR_COUNTER.labels(method=func.__name__, endpoint=method_name, error_type=type(e).__name__).inc()
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
