import os
import time
import functools
import psutil
import psycopg2
import threading
from dotenv import load_dotenv
from typing import List, Dict, Any
from contextlib import contextmanager

def get_db_config():
    """Get database configuration from environment variables."""
    # Load environment variables when actually needed
    load_dotenv()
    
    try:
        return {
            'host': os.environ['DB_HOST'],
            'port': os.environ['DB_PORT'],
            'dbname': os.environ['DB_NAME'],
            'user': os.environ['DB_USER'],
            'password': os.environ['DB_PASSWORD']
        }
    except KeyError as e:
        raise ValueError(f"Missing required environment variable: {e}. Please check your .env file.")

def openai_token_usage(response):
    """
    Unified extractor for OpenAI responses
    """
    model = None
    prompt = None
    completion = None
    total = None

    if hasattr(response, "model") and hasattr(response, "usage"):
        model = getattr(response, "model", None)
        usage = getattr(response, "usage", None)
        if usage:
            prompt = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
            completion = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)
            total = getattr(usage, "total_tokens", None)
        return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

    if isinstance(response, dict):
        model = response.get("model")
        usage = response.get("usage", {}) or {}
        prompt = usage.get("prompt_tokens") or usage.get("input_tokens")
        completion = usage.get("completion_tokens") or usage.get("output_tokens")
        total = usage.get("total_tokens")
        return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

    raise ValueError("Unsupported response object: model or usage not found")


class TokenTracker:
    """Context manager that automatically tracks OpenAI calls"""
    
    def __init__(self, request_id: str, function_name: str):
        self.request_id = request_id
        self.function_name = function_name
        self.responses = []
        self.original_methods = {}
        self.call_stack = []  # Track which function made each call
    
    def __enter__(self):
        # Import here to avoid circular imports
        try:
            from openai import OpenAI
            from openai.resources.chat import completions
            from openai.resources import embeddings
            import inspect
            
            # Store original methods
            self.original_chat_create = completions.Completions.create
            self.original_embeddings_create = embeddings.Embeddings.create
            
            # Create wrapper functions that track the calling function
            def chat_wrapper(self_inner, *args, **kwargs):
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_chat_create(self_inner, *args, **kwargs)
                self.responses.append(response)
                self.call_stack.append(calling_function)
                return response
            
            def embeddings_wrapper(self_inner, *args, **kwargs):
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_embeddings_create(self_inner, *args, **kwargs)
                self.responses.append(response)
                self.call_stack.append(calling_function)
                return response
            
            # Monkey patch the methods GLOBALLY (this is key!)
            completions.Completions.create = chat_wrapper
            embeddings.Embeddings.create = embeddings_wrapper
            
        except ImportError:
            pass  # OpenAI not available
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        try:
            from openai.resources.chat import completions
            from openai.resources import embeddings
            
            completions.Completions.create = self.original_chat_create
            embeddings.Embeddings.create = self.original_embeddings_create
        except:
            pass
        
        # Log all collected responses with their calling functions
        for i, (response, calling_function) in enumerate(zip(self.responses, self.call_stack)):
            try:
                usage = openai_token_usage(response)
                if usage:
                    # Create descriptive function names based on where the call was made
                    if calling_function == self.function_name:
                        # Direct call from decorated function
                        function_name = f"{self.function_name}_call_{i+1}" if len(self.responses) > 1 else self.function_name
                    else:
                        # Call from nested function
                        function_name = f"{self.function_name}_{calling_function}_call_{i+1}"
                    
                    log_token_usage_to_db(self.request_id, function_name, usage)
            except Exception as e:
                print(f"Error tracking token usage for call {i+1}: {e}")


def track_token_usage(request_id):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with TokenTracker(request_id, func.__name__):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


def log_token_usage_to_db(request_id, function_name, usage):
    db_config = get_db_config()  # Get config when actually needed
    conn = psycopg2.connect(**db_config)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO token_usage (
                    request_id,
                    function_name,
                    model,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, ( 
                request_id,
                function_name,
                usage['model'],
                usage['prompt_tokens'],
                usage['completion_tokens'],
                usage['total_tokens'],
            ))
    conn.close()


# Resource tracking functions (unchanged)
def get_process():
    return psutil.Process(os.getpid())

def get_memory_gb(process):
    """Returns memory in GB from RSS (resident set size)"""
    return process.memory_info().rss / (1024 ** 3)

def log_to_db(request_id, function_name, duration, cpu_seconds, gb_seconds):
    db_config = get_db_config()  # Get config when actually needed
    conn = psycopg2.connect(**db_config)
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO request_metrics (
                    request_id,
                    function_name,
                    duration_sec,
                    cpu_seconds,
                    gb_seconds,
                    timestamp
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                request_id,
                function_name,
                duration,
                cpu_seconds,
                gb_seconds
            ))
    conn.close()


def track_resources_db(request_id):
    """
    Decorator that tracks CPU-seconds and GB-seconds used by a function
    and logs it into a PostgreSQL database.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = get_process()
            mem_samples = []

            def sample_memory():
                while not stop_event.is_set():
                    mem_samples.append(get_memory_gb(process))
                    time.sleep(0.1)

            stop_event = threading.Event()
            sampler = threading.Thread(target=sample_memory)
            sampler.start()

            start_time = time.time()
            cpu_time_start = process.cpu_times().user + process.cpu_times().system

            result = func(*args, **kwargs)

            end_time = time.time()
            cpu_time_end = process.cpu_times().user + process.cpu_times().system
            stop_event.set()
            sampler.join()

            duration = end_time - start_time
            cpu_seconds = cpu_time_end - cpu_time_start

            avg_memory_gb = sum(mem_samples) / len(mem_samples) if mem_samples else 0
            gb_seconds = avg_memory_gb * duration

            log_to_db(request_id, func.__name__, duration, cpu_seconds, gb_seconds)

            return result
        return wrapper
    return decorator