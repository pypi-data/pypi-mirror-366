"""
GoFastAPI - High-performance hybrid Go/Python web framework
A drop-in replacement for FastAPI with 25x better performance

Drop-in FastAPI compatibility:
    from gofastapi import FastAPI  # Instead of: from fastapi import FastAPI
    
    app = FastAPI()  # Same API, 25x faster performance!
"""

__version__ = "1.0.2"
__author__ = "GoFastAPI Team"
__email__ = "team@gofastapi.dev"

from .core import GoFastAPI

# Import runtime components
from .runtime import SubinterpreterManager, HotReloader, PythonBridge

# Import CLI
from .cli import CLI

# Import monitoring tools
from .monitoring import MetricsCollector, HealthChecker

# Import AI debugging tools
from .ai_debugger import ErrorTranslator, PerformanceAnalyzer

# FastAPI compatibility aliases for drop-in replacement
FastAPI = GoFastAPI  # Main compatibility alias
App = GoFastAPI      # Alternative alias

# Common FastAPI imports for compatibility
from .core import (
    Request, Response, HTTPException, Depends,
    status, Form, File, UploadFile, Cookie, Header,
    Path, Query, Body, Security
)

__all__ = [
    # Main classes
    "GoFastAPI",
    "FastAPI",  # FastAPI compatibility
    "App",      # Alternative alias
    
    # Runtime components
    "SubinterpreterManager", 
    "HotReloader",
    "PythonBridge",
    
    # Tools
    "CLI",
    "MetricsCollector",
    "HealthChecker", 
    "ErrorTranslator",
    "PerformanceAnalyzer",
    
    # FastAPI compatibility imports
    "Request",
    "Response", 
    "HTTPException",
    "Depends",
    "status",
    "Form",
    "File",
    "UploadFile",
    "Cookie",
    "Header",
    "Path",
    "Query",
    "Body",
    "Security"
]