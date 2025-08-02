"""
GoFastAPI AI Debugger Module
AI-powered debugging and performance analysis
"""

class ErrorTranslator:
    """Translates errors into human-readable explanations."""
    
    def __init__(self):
        self.translations = {}
    
    def translate(self, error: Exception):
        """Translate an error into a readable explanation."""
        error_type = type(error).__name__
        return f"Error type: {error_type}, Message: {str(error)}"


class PerformanceAnalyzer:
    """Analyzes application performance."""
    
    def __init__(self):
        self.measurements = []
    
    def measure(self, operation_name: str, duration: float):
        """Record a performance measurement."""
        self.measurements.append({
            "operation": operation_name,
            "duration": duration
        })
    
    def get_analysis(self):
        """Get performance analysis."""
        if not self.measurements:
            return "No performance data available"
        
        avg_duration = sum(m["duration"] for m in self.measurements) / len(self.measurements)
        return f"Average operation duration: {avg_duration:.3f}ms"
