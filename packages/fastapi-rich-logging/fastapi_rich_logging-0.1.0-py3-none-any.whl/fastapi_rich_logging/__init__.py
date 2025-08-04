init_py = '''
"""FastAPI Rich Logging - Beautiful request/response logging middleware."""

from .middleware import RichLoggingMiddleware, SimpleRichLoggingMiddleware
from .formatters import create_rich_formatter

__version__ = "0.1.0"
__all__ = ["RichLoggingMiddleware", "SimpleRichLoggingMiddleware", "create_rich_formatter"]
'''
