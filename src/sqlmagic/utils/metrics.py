import time
import logging
from functools import wraps
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "queries_executed": 0,
            "connections_created": 0,
            "errors": 0,
            "avg_query_time": 0.0
        }
        self.query_times = []
    
    def record_query(self, duration: float):
        self.metrics["queries_executed"] += 1
        self.query_times.append(duration)
        self.metrics["avg_query_time"] = sum(self.query_times) / len(self.query_times)
    
    def record_connection(self):
        self.metrics["connections_created"] += 1
    
    def record_error(self):
        self.metrics["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()

metrics = MetricsCollector()

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            metrics.record_query(duration)
            logger.debug(f"{func.__name__} took {duration:.3f}s")
            return result
        except Exception as e:
            metrics.record_error()
            raise
    return wrapper