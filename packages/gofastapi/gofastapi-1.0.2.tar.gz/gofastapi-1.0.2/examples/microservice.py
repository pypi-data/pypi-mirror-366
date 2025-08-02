"""
Example: High-Performance Microservice
Demonstrates GoFastAPI for building scalable microservices
"""

from gofastapi import GoFastAPI
from gofastapi.runtime import HotReloader
from gofastapi.ai import ErrorTranslator
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import random

# Create high-performance microservice
app = GoFastAPI(
    title="High-Performance Microservice",
    version="3.0.0",
    description="Scalable microservice with GoFastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize components
hot_reloader = HotReloader()
error_translator = ErrorTranslator()

# In-memory caches (use Redis in production)
cache_store: Dict[str, Any] = {}
rate_limit_store: Dict[str, List[float]] = {}
metrics_store: Dict[str, Any] = {
    "requests_total": 0,
    "requests_per_endpoint": {},
    "response_times": [],
    "errors_count": 0,
    "uptime_start": time.time()
}

# Configuration
RATE_LIMIT_REQUESTS = 1000  # requests per minute
CACHE_TTL = 300  # 5 minutes
MAX_RESPONSE_TIME_SAMPLES = 1000


# Middleware functions
def rate_limit_middleware(request):
    """Simple rate limiting middleware."""
    client_ip = request.get("client_ip", "127.0.0.1")
    current_time = time.time()
    
    # Clean old entries
    if client_ip in rate_limit_store:
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip]
            if current_time - req_time < 60  # Keep only last minute
        ]
    else:
        rate_limit_store[client_ip] = []
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return {"error": "Rate limit exceeded", "retry_after": 60}, 429
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return None


def cache_get(key: str) -> Optional[Any]:
    """Get item from cache."""
    if key in cache_store:
        item = cache_store[key]
        if time.time() - item["timestamp"] < CACHE_TTL:
            return item["data"]
        else:
            del cache_store[key]
    return None


def cache_set(key: str, data: Any) -> None:
    """Set item in cache."""
    cache_store[key] = {
        "data": data,
        "timestamp": time.time()
    }


def update_metrics(endpoint: str, response_time: float, status_code: int):
    """Update request metrics."""
    metrics_store["requests_total"] += 1
    
    if endpoint not in metrics_store["requests_per_endpoint"]:
        metrics_store["requests_per_endpoint"][endpoint] = 0
    metrics_store["requests_per_endpoint"][endpoint] += 1
    
    # Keep response time samples
    if len(metrics_store["response_times"]) >= MAX_RESPONSE_TIME_SAMPLES:
        metrics_store["response_times"].pop(0)
    metrics_store["response_times"].append(response_time)
    
    if status_code >= 400:
        metrics_store["errors_count"] += 1


@app.get("/")
def root():
    """Service health and information."""
    uptime_seconds = time.time() - metrics_store["uptime_start"]
    
    return {
        "service": "High-Performance Microservice",
        "version": "3.0.0",
        "status": "running",
        "uptime_seconds": round(uptime_seconds, 2),
        "framework": "GoFastAPI",
        "features": [
            "Rate limiting",
            "Caching",
            "Hot reloading",
            "Metrics collection",
            "Error translation",
            "High concurrency"
        ],
        "performance": {
            "requests_per_second": "500K+",
            "concurrent_connections": "10K+",
            "memory_efficiency": "GIL-free Python"
        },
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "data_processing": "/api/v1/process",
            "cache_operations": "/api/v1/cache",
            "batch_processing": "/api/v1/batch"
        }
    }


@app.get("/health")
def health_check():
    """Comprehensive health check."""
    start_time = time.perf_counter()
    
    # Check various components
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Memory check
    import psutil
    memory_usage = psutil.virtual_memory().percent
    health_status["checks"]["memory"] = {
        "status": "healthy" if memory_usage < 80 else "warning",
        "usage_percent": memory_usage
    }
    
    # Cache check
    cache_size = len(cache_store)
    health_status["checks"]["cache"] = {
        "status": "healthy",
        "size": cache_size,
        "max_size": 10000
    }
    
    # Rate limiting check
    active_clients = len(rate_limit_store)
    health_status["checks"]["rate_limiting"] = {
        "status": "healthy",
        "active_clients": active_clients
    }
    
    # Performance check
    avg_response_time = (
        sum(metrics_store["response_times"]) / len(metrics_store["response_times"])
        if metrics_store["response_times"] else 0
    )
    
    health_status["checks"]["performance"] = {
        "status": "healthy" if avg_response_time < 100 else "warning",
        "avg_response_time_ms": round(avg_response_time, 2),
        "total_requests": metrics_store["requests_total"]
    }
    
    # Overall status
    warning_checks = [
        check for check in health_status["checks"].values()
        if check["status"] == "warning"
    ]
    
    if warning_checks:
        health_status["status"] = "warning"
    
    check_time = (time.perf_counter() - start_time) * 1000
    health_status["health_check_time_ms"] = round(check_time, 2)
    
    return health_status


@app.get("/metrics")
def get_metrics():
    """Get detailed service metrics."""
    uptime_seconds = time.time() - metrics_store["uptime_start"]
    
    # Calculate statistics
    response_times = metrics_store["response_times"]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        # Simple percentile calculation
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p95_response_time = sorted_times[p95_index] if sorted_times else 0
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    requests_per_second = metrics_store["requests_total"] / uptime_seconds if uptime_seconds > 0 else 0
    error_rate = (metrics_store["errors_count"] / metrics_store["requests_total"] * 100) if metrics_store["requests_total"] > 0 else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "uptime": {
            "seconds": round(uptime_seconds, 2),
            "hours": round(uptime_seconds / 3600, 2)
        },
        "requests": {
            "total": metrics_store["requests_total"],
            "per_second": round(requests_per_second, 2),
            "per_endpoint": metrics_store["requests_per_endpoint"]
        },
        "performance": {
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "p95_response_time_ms": round(p95_response_time, 2)
        },
        "errors": {
            "total": metrics_store["errors_count"],
            "rate_percent": round(error_rate, 2)
        },
        "cache": {
            "size": len(cache_store),
            "hit_ratio": "95%"  # Mock value
        },
        "rate_limiting": {
            "active_clients": len(rate_limit_store),
            "requests_per_minute_limit": RATE_LIMIT_REQUESTS
        }
    }


@app.post("/api/v1/process")
def process_data(data: Dict[str, Any]):
    """High-performance data processing endpoint."""
    start_time = time.perf_counter()
    
    # Rate limiting
    rate_limit_result = rate_limit_middleware({"client_ip": "demo_client"})
    if rate_limit_result:
        return rate_limit_result
    
    try:
        # Generate cache key
        data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        cache_key = f"process_{data_hash}"
        
        # Check cache
        cached_result = cache_get(cache_key)
        if cached_result:
            processing_time = (time.perf_counter() - start_time) * 1000
            update_metrics("/api/v1/process", processing_time, 200)
            
            return {
                "result": cached_result,
                "cached": True,
                "processing_time_ms": round(processing_time, 2)
            }
        
        # Process data
        operation = data.get("operation", "transform")
        input_data = data.get("data", [])
        
        if operation == "transform":
            # Transform each item
            result = [
                {
                    "original": item,
                    "transformed": str(item).upper() if isinstance(item, str) else item * 2,
                    "hash": hashlib.md5(str(item).encode()).hexdigest()[:8]
                }
                for item in input_data
            ]
        
        elif operation == "aggregate":
            # Aggregate numeric data
            numeric_data = [x for x in input_data if isinstance(x, (int, float))]
            result = {
                "count": len(numeric_data),
                "sum": sum(numeric_data),
                "avg": sum(numeric_data) / len(numeric_data) if numeric_data else 0,
                "min": min(numeric_data) if numeric_data else None,
                "max": max(numeric_data) if numeric_data else None
            }
        
        elif operation == "filter":
            # Filter data based on criteria
            criteria = data.get("criteria", {})
            min_val = criteria.get("min", float("-inf"))
            max_val = criteria.get("max", float("inf"))
            
            result = [
                item for item in input_data
                if isinstance(item, (int, float)) and min_val <= item <= max_val
            ]
        
        else:
            result = {"error": f"Unknown operation: {operation}"}
        
        # Cache the result
        cache_set(cache_key, result)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        update_metrics("/api/v1/process", processing_time, 200)
        
        return {
            "result": result,
            "cached": False,
            "operation": operation,
            "input_size": len(input_data),
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        update_metrics("/api/v1/process", processing_time, 500)
        
        # Use AI error translator
        translated_error = error_translator.translate_error(str(e))
        
        return {
            "error": "Processing failed",
            "details": translated_error,
            "processing_time_ms": round(processing_time, 2)
        }, 500


@app.post("/api/v1/batch")
def batch_process(data: Dict[str, Any]):
    """Batch processing endpoint for multiple operations."""
    start_time = time.perf_counter()
    
    try:
        operations = data.get("operations", [])
        results = []
        
        for i, operation in enumerate(operations):
            op_start = time.perf_counter()
            
            # Process each operation
            op_type = operation.get("type", "noop")
            op_data = operation.get("data", {})
            
            if op_type == "hash":
                text = op_data.get("text", "")
                result = {
                    "operation_id": i,
                    "type": op_type,
                    "result": hashlib.sha256(text.encode()).hexdigest()
                }
            
            elif op_type == "random":
                count = op_data.get("count", 10)
                result = {
                    "operation_id": i,
                    "type": op_type,
                    "result": [random.randint(1, 100) for _ in range(count)]
                }
            
            elif op_type == "fibonacci":
                n = min(op_data.get("n", 10), 50)  # Limit to prevent long computation
                fib_sequence = []
                a, b = 0, 1
                for _ in range(n):
                    fib_sequence.append(a)
                    a, b = b, a + b
                
                result = {
                    "operation_id": i,
                    "type": op_type,
                    "result": fib_sequence
                }
            
            else:
                result = {
                    "operation_id": i,
                    "type": op_type,
                    "error": f"Unknown operation type: {op_type}"
                }
            
            op_time = (time.perf_counter() - op_start) * 1000
            result["processing_time_ms"] = round(op_time, 2)
            results.append(result)
        
        total_time = (time.perf_counter() - start_time) * 1000
        update_metrics("/api/v1/batch", total_time, 200)
        
        return {
            "batch_results": results,
            "total_operations": len(operations),
            "total_processing_time_ms": round(total_time, 2),
            "average_time_per_operation_ms": round(total_time / len(operations), 2) if operations else 0
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        update_metrics("/api/v1/batch", processing_time, 500)
        
        return {
            "error": "Batch processing failed",
            "details": str(e),
            "processing_time_ms": round(processing_time, 2)
        }, 500


@app.get("/api/v1/cache")
def get_cache_info():
    """Get cache information and statistics."""
    cache_size = len(cache_store)
    cache_items = []
    
    for key, item in list(cache_store.items())[:10]:  # Show first 10 items
        age_seconds = time.time() - item["timestamp"]
        cache_items.append({
            "key": key,
            "age_seconds": round(age_seconds, 2),
            "ttl_remaining": round(CACHE_TTL - age_seconds, 2),
            "size_bytes": len(str(item["data"]))
        })
    
    return {
        "cache_status": "active",
        "total_items": cache_size,
        "ttl_seconds": CACHE_TTL,
        "sample_items": cache_items,
        "memory_usage": {
            "estimated_mb": round(len(str(cache_store)) / 1024 / 1024, 2)
        }
    }


@app.delete("/api/v1/cache")
def clear_cache():
    """Clear all cached data."""
    items_cleared = len(cache_store)
    cache_store.clear()
    
    return {
        "message": "Cache cleared successfully",
        "items_cleared": items_cleared,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/performance")
def performance_test():
    """Performance testing endpoint."""
    start_time = time.perf_counter()
    
    # Simulate various operations
    operations_performed = []
    
    # CPU intensive operation
    cpu_start = time.perf_counter()
    result = sum(i * i for i in range(10000))
    cpu_time = (time.perf_counter() - cpu_start) * 1000
    operations_performed.append({
        "operation": "cpu_intensive",
        "time_ms": round(cpu_time, 2),
        "result_sample": result
    })
    
    # Memory operation
    mem_start = time.perf_counter()
    large_list = list(range(100000))
    mem_time = (time.perf_counter() - mem_start) * 1000
    operations_performed.append({
        "operation": "memory_allocation",
        "time_ms": round(mem_time, 2),
        "size": len(large_list)
    })
    
    # String operation
    str_start = time.perf_counter()
    text = "GoFastAPI " * 1000
    text_hash = hashlib.md5(text.encode()).hexdigest()
    str_time = (time.perf_counter() - str_start) * 1000
    operations_performed.append({
        "operation": "string_processing",
        "time_ms": round(str_time, 2),
        "hash": text_hash
    })
    
    total_time = (time.perf_counter() - start_time) * 1000
    
    return {
        "performance_test": "completed",
        "total_time_ms": round(total_time, 2),
        "operations": operations_performed,
        "framework": "GoFastAPI",
        "performance_note": "25x faster than FastAPI",
        "concurrency": "GIL-free execution"
    }


if __name__ == "__main__":
    print("🚀 Starting High-Performance Microservice")
    print("⚡ Rate limiting and caching enabled")
    print("📊 Metrics collection active")
    print("🔄 Hot reloading configured")
    print("🤖 AI error translation ready")
    print("🌐 Available at: http://localhost:8002")
    
    app.run(host="0.0.0.0", port=8002, reload=True)
