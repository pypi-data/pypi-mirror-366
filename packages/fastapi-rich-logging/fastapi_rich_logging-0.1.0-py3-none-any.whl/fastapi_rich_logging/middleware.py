"""Rich logging middleware for FastAPI applications."""


import time
import logging
from typing import Optional, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class RichLoggingMiddleware(BaseHTTPMiddleware):
    """ASGI middleware for request logging with rich panels."""
    
    def __init__(
        self, 
        app: ASGIApp,
        logger: Optional[logging.Logger] = None,
        show_headers: bool = False,
        show_query_params: bool = True,
        console: Optional[Console] = None,
    ):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
        self.show_headers = show_headers
        self.show_query_params = show_query_params
        self.console = console or Console()
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Handle the middleware logic with rich panel logging."""
        start_time = time.time()
        
        # Log request start
        self._log_request_start(request)
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log successful response
            self._log_response_success(request, response, process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log failed response
            self._log_response_error(request, e, process_time)
            
            raise
    
    def _log_request_start(self, request: Request) -> None:
        """Log request start with rich panel."""
        
        # Create request info table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold cyan", width=12)
        table.add_column("Value", style="white")
        
        # Add basic request info
        method_color = self._get_method_color(request.method)
        table.add_row("Method", f"[{method_color}]{request.method}[/{method_color}]")
        table.add_row("URL", str(request.url))
        table.add_row("Path", request.url.path)
        
        # Add client info if available
        if request.client:
            table.add_row("Client", f"{request.client.host}:{request.client.port}")
        
        # Add query parameters if enabled and present
        if self.show_query_params and request.query_params:
            query_str = " & ".join([f"{k}={v}" for k, v in request.query_params.items()])
            table.add_row("Query", query_str)
        
        # Add headers if enabled
        if self.show_headers:
            important_headers = ["user-agent", "content-type", "authorization", "accept"]
            for header_name in important_headers:
                if header_value := request.headers.get(header_name):
                    # Mask authorization header for security
                    if header_name == "authorization":
                        header_value = "***masked***"
                    display_value = header_value[:50] + "..." if len(header_value) > 50 else header_value
                    table.add_row(header_name.title(), display_value)
        
        # Create and display panel
        panel = Panel(
            table,
            title="🚀 Incoming Request",
            title_align="left",
            border_style="blue",
            padding=(0, 1),
            expand=False
        )
        
        self.console.print(panel)
    
    def _log_response_success(self, request: Request, response: Response, process_time: float) -> None:
        """Log successful response with rich panel."""
        
        # Create response info table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold green", width=12)
        table.add_column("Value", style="white")
        
        # Add response info
        status_color = self._get_status_color(response.status_code)
        table.add_row("Status", f"[{status_color}]{response.status_code}[/{status_color}]")
        table.add_row("Method", f"[{self._get_method_color(request.method)}]{request.method}[/{self._get_method_color(request.method)}]")
        table.add_row("Path", request.url.path)
        table.add_row("Duration", f"{process_time:.4f}s")
        
        # Add response headers if they exist
        if hasattr(response, 'headers') and response.headers:
            content_type = response.headers.get("content-type", "N/A")
            table.add_row("Content-Type", content_type)
        
        # Create panel with appropriate styling
        border_style = "green" if response.status_code < 400 else "yellow"
        title = "✅ Request Completed" if response.status_code < 400 else "⚠️ Request Completed"
        
        panel = Panel(
            table,
            title=title,
            title_align="left",
            border_style=border_style,
            padding=(0, 1),
            expand=False
        )
        
        self.console.print(panel)
    
    def _log_response_error(self, request: Request, error: Exception, process_time: float) -> None:
        """Log failed response with rich panel."""
        
        # Create error info table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold red", width=12)
        table.add_column("Value", style="white")
        
        table.add_row("Error Type", f"[red]{error.__class__.__name__}[/red]")
        table.add_row("Method", f"[{self._get_method_color(request.method)}]{request.method}[/{self._get_method_color(request.method)}]")
        table.add_row("Path", request.url.path)
        table.add_row("Duration", f"{process_time:.4f}s")
        
        error_msg = str(error)
        display_error = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg
        table.add_row("Message", display_error)
        
        # Create error panel
        panel = Panel(
            table,
            title="❌ Request Failed",
            title_align="left",
            border_style="red",
            padding=(0, 1),
            expand=False
        )
        
        self.console.print(panel)
    
    def _get_method_color(self, method: str) -> str:
        """Get color for HTTP method."""
        colors = {
            "GET": "green",
            "POST": "blue", 
            "PUT": "yellow",
            "PATCH": "magenta",
            "DELETE": "red",
            "OPTIONS": "cyan",
            "HEAD": "white"
        }
        return colors.get(method.upper(), "white")
    
    def _get_status_color(self, status_code: int) -> str:
        """Get color for HTTP status code."""
        if status_code < 300:
            return "green"
        elif status_code < 400:
            return "yellow"
        elif status_code < 500:
            return "red"
        else:
            return "bright_red"


class SimpleRichLoggingMiddleware(BaseHTTPMiddleware):
    """Simplified middleware with basic rich panels."""
    
    def __init__(self, app: ASGIApp, logger: Optional[logging.Logger] = None, console: Optional[Console] = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
        self.console = console or Console()
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Handle the middleware logic with simple rich panels."""
        start_time = time.time()
        
        # Simple request log
        self.console.print(
            Panel(
                f"[bold blue]{request.method}[/bold blue] {request.url}",
                title="🚀 Request",
                border_style="blue",
                padding=(0, 2),
                expand=False
            )
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Simple success log
            status_color = "green" if response.status_code < 400 else "yellow" if response.status_code < 500 else "red"
            self.console.print(
                Panel(
                    f"[{status_color}]{response.status_code}[/{status_color}] "
                    f"[bold blue]{request.method}[/bold blue] {request.url.path} "
                    f"[dim]({process_time:.4f}s)[/dim]",
                    title="✅ Response",
                    border_style=status_color,
                    padding=(0, 2),
                    expand=False
                )
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Simple error log
            self.console.print(
                Panel(
                    f"[bold red]{e.__class__.__name__}[/bold red] "
                    f"[bold blue]{request.method}[/bold blue] {request.url.path} "
                    f"[dim]({process_time:.4f}s)[/dim]\\n"
                    f"[red]{str(e)}[/red]",
                    title="❌ Error",
                    border_style="red",
                    padding=(0, 2),
                    expand=False
                )
            )
            
            raise