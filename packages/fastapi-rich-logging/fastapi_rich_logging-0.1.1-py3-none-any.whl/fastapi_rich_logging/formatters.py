"""Rich formatters for FastAPI logging."""

from typing import Callable, Optional, Dict, Any
from fastapi import Request
from rich.console import Console


def create_rich_formatter(console: Optional[Console] = None) -> Callable[[Exception, Dict[str, Any], Request], Dict[str, Any]]:
    """Create a Rich formatter for custom error handling."""
    
    if console is None:
        console = Console()
    
    def formatter(exc: Exception, content: Dict[str, Any], request: Request) -> Dict[str, Any]:
        """Format error responses with Rich console output."""
        try:
            from rich.panel import Panel
            
            console.print(
                Panel(
                    f"[bold red]Error:[/bold red] {exc.__class__.__name__}\\n"
                    f"[bold yellow]Status Code:[/bold yellow] {content.get('status_code', 'Unknown')}\\n"
                    f"[bold green]Detail:[/bold green] {content['detail']}\\n"
                    f"[bold blue]Path:[/bold blue] {request.method} {request.url}",
                    title="API Exception",
                    title_align="left",
                    border_style="red",
                    padding=(1, 2),
                    expand=False,
                )
            )
        except ImportError:
            # Fallback if rich is not available
            pass
        
        return content
    
    return formatter