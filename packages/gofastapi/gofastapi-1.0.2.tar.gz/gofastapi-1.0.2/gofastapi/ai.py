"""
GoFastAPI AI Module
AI-powered features for GoFastAPI (alias for ai_debugger)
"""

# Re-export from ai_debugger for compatibility
from .ai_debugger import ErrorTranslator, PerformanceAnalyzer

__all__ = ["ErrorTranslator", "PerformanceAnalyzer"]
