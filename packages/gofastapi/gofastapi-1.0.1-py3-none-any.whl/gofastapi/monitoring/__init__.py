"""
GoFastAPI Monitoring Module
Health checking and metrics collection
"""

class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, metric_name: str, value: int = 1):
        """Increment a metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += value
    
    def get_metrics(self):
        """Get all collected metrics."""
        return self.metrics


class HealthChecker:
    """Performs health checks on the application."""
    
    def __init__(self):
        self.checks = []
    
    def add_check(self, name: str, check_func):
        """Add a health check."""
        self.checks.append({"name": name, "check": check_func})
    
    def run_checks(self):
        """Run all health checks."""
        results = {}
        for check in self.checks:
            try:
                results[check["name"]] = check["check"]()
            except Exception as e:
                results[check["name"]] = f"Error: {e}"
        return results
