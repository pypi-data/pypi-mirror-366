
import functools
import time
import requests
import json
from datetime import datetime
from typing import Any, Callable
import hashlib
import inspect
import base64
import io
from PIL import Image

API_BASE_URL = "https://unscale.replit.app/api"


def trace(project_id: str, name: str = None, version: str = None):
    """
    Decorator to trace function execution and send metadata to the API.

    Args:
        project_id: The project ID for tracing.
        name: Optional function name override.
        version: Optional version string.
    """
    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = f"trace_{int(time.time() * 1000)}_{hash(str(args) + str(kwargs)) % 10000}"
            wrapper.last_trace_id = trace_id  # <-- Set last_trace_id on wrapper

            actual_name = name or func.__name__

            try:
                source = inspect.getsource(func)
                feature_hash = hashlib.md5(source.encode()).hexdigest()[:8]
                function_code_snippet = source[:500] + ("..." if len(source) > 500 else "")
            except Exception:
                source = ""
                feature_hash = "unknown"
                function_code_snippet = "Source unavailable"

            def serialize_value(val: Any):
                if isinstance(val, (str, int, float, bool)):
                    return val
                elif isinstance(val, Image.Image):
                    buffer = io.BytesIO()
                    val.save(buffer, format='PNG')
                    img_str = base64.b64encode(buffer.getvalue()).decode()
                    return f"data:image/png;base64,{img_str}"
                else:
                    return None  # skip complex types

            # Serialize inputs but only allowed types
            inputs = {}
            for i, arg in enumerate(args):
                v = serialize_value(arg)
                if v is not None:
                    inputs[f"arg_{i}"] = v
            for k, v in kwargs.items():
                sv = serialize_value(v)
                if sv is not None:
                    inputs[k] = sv

            start_time = time.time()
            error_occurred = False
            output = None
            try:
                output = func(*args, **kwargs)
                if not isinstance(output, (str, int, float, bool, Image.Image)):
                    raise TypeError("Output must be bool, number, string, or PIL.Image.Image")
                output_serialized = serialize_value(output)
                return output
            except Exception as e:
                error_occurred = True
                output_serialized = None
                output = str(e)
                raise
            finally:
                latency = time.time() - start_time

                payload = {
                    "project_id": project_id,
                    "trace_id": trace_id,
                    "function_name": actual_name,
                    "function_hash": feature_hash,
                    "function_code_snippet": function_code_snippet,
                    "input": inputs,
                    "output": output_serialized,
                    "error": error_occurred,
                    "latency": latency,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                try:
                    response = requests.post(f"{API_BASE_URL}/upload_trace", json=payload, timeout=5)
                    if response.status_code != 200:
                        print(f"Warning: Failed to log trace for {actual_name}: {response.text}")
                except Exception as exc:
                    print(f"Warning: Trace API call failed: {exc}")

        wrapper.last_trace_id = None  # Initialize attribute
        return wrapper

    return decorator


def feedback(project_id: str, function_name: str, trace_id: str, rating: int):
    """
    Send rating feedback for a trace.

    Args:
        project_id: Your project ID.
        function_name: Function name string, required by backend.
        trace_id: The trace ID to update.
        rating: Integer rating value (e.g., 1-5 scale).
    """
    payload = {
        "project_id": project_id,
        "trace_id": trace_id,
        "function_name": function_name,
        "rating": rating,
    }
    print(f"DEBUG: Sending feedback - project_id={project_id}, trace_id={trace_id}, function_name={function_name}, rating={rating}")
    try:
        response = requests.post(f"{API_BASE_URL}/trace_feedback", json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Warning: Failed to update rating: {response.text}")
            print(f"Response status: {response.status_code}")
        else:
            print(f"Successfully updated rating for trace {trace_id} to {rating}")
    except Exception as exc:
        print(f"Warning: Rating API call failed: {exc}")
