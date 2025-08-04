"""Command-line interface module for OpenAPI Scanner.

This module provides the command-line interface for scanning APIs based on OpenAPI specifications.
It handles file loading, authentication, and coordinates the scanning process.
"""
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel

from specphp_scanner.auth.factory import AuthFactory
from specphp_scanner.core.scanner import scan_api
from specphp_scanner.utils.report import ReportFormat, generate_report

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Change default level to WARNING
    format='%(levelname)s: %(message)s'  # Simplify log format
)
logger = logging.getLogger(__name__)

console = Console()
app = typer.Typer()

def load_spec_file(file_path: Path) -> Dict[str, Any]:
    """Load OpenAPI specification from JSON or YAML file.
    
    Args:
        file_path: Path to the specification file
        
    Returns:
        Dict containing the OpenAPI specification
        
    Raises:
        FileNotFoundError: If the specification file does not exist
        ValueError: If the file format is not supported or the file is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Specification file not found: {file_path}")
        
    try:
        with open(file_path) as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid specification file: {e}")

@app.command()
def main(
    spec_file: Path = typer.Argument(
        ...,
        help="Path to the OpenAPI specification file (JSON or YAML)",
    ),
    host: str = typer.Option(
        ...,
        "--host",
        "-h",
        help="Target host"
    ),
    port: int = typer.Option(
        ...,
        "--port",
        "-p",
        help="Target port"
    ),
    auth_class: Optional[str] = typer.Option(
        None,
        "--auth-class",
        "-a",
        help="Full path to the authentication class (e.g. 'examples.koel.auth.KoelAuth')"
    ),
    no_replace_params: bool = typer.Option(
        False,
        "--no-replace-params",
        help="Disable path parameter replacement"
    ),
    auth_params: Optional[str] = typer.Option(
        None,
        "--auth-params",
        help="JSON string containing authentication parameters"
    ),
    headers: Optional[str] = typer.Option(
        None,
        "--headers",
        help="JSON string containing custom headers to include in all requests"
    ),
    output_format: ReportFormat = typer.Option(
        ReportFormat.CONSOLE,
        "--output-format",
        "-o",
        help="Output format for the scan report (console, html, csv, jsonl)"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output-file",
        "-f",
        help="Output file path for the report (required for non-console formats)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
) -> None:
    """Run the API scanner with configurable path parameter replacement.
    
    Args:
        spec_file: Path to the OpenAPI specification file
        auth_class: Path to the authentication class
        host: Target host
        port: Target port
        no_replace_params: Whether to disable path parameter replacement
        auth_params: JSON string containing authentication parameters
        headers: JSON string containing custom headers
        output_format: Format for the scan report
        output_file: Path to save the report (required for non-console formats)
        verbose: Whether to enable verbose logging
    """
    # Set logging level based on verbose flag
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    
    # Validate output options
    if output_format != ReportFormat.CONSOLE and not output_file:
        raise typer.BadParameter("Output file is required for non-console formats")
    
    # Validate spec_file parameter
    if not spec_file:
        raise typer.Exit()
    
    # Load OpenAPI spec
    try:
        data = load_spec_file(spec_file)
    except (FileNotFoundError, ValueError) as e:
        raise typer.BadParameter(str(e))
    
    # Initialize auth instance
    auth = None
    if auth_class:
        # Parse auth parameters
        auth_kwargs: Dict[str, Any] = {}
        if auth_params:
            try:
                auth_kwargs = json.loads(auth_params)
            except json.JSONDecodeError:
                raise typer.BadParameter("Invalid JSON in auth-params")
        
        # Create auth instance
        try:
            auth = AuthFactory.create(auth_class, **auth_kwargs)
        except ValueError as e:
            raise typer.BadParameter(str(e))
    
    # Get headers and cookies
    headers_dict: Dict[str, str] = {}
    cookies: Dict[str, str] = {}
    
    # Add custom headers if specified
    if headers:
        try:
            headers_dict.update(json.loads(headers))
        except json.JSONDecodeError:
            raise typer.BadParameter("Invalid JSON in headers")
    
    # Add auth headers if authentication is enabled
    if auth:
        try:
            base_url = f"http://{host}:{port}"
            headers_dict.update(auth.get_headers(base_url))
            cookies = auth.get_cookies(base_url)
        except Exception as e:
            console.print(f"[red]Authentication failed: {str(e)}[/red]")
            raise typer.Exit(1)
    
    # Run the scanner
    try:
        results = scan_api(
            host=host,
            port=port,
            headers=headers_dict,
            cookies=cookies,
            data=data,
            replace_params=not no_replace_params
        )
        
        if not results:
            console.print("[yellow]No API endpoints found in the specification[/yellow]")
            return
            
        # Generate report
        if output_format != ReportFormat.CONSOLE:
            try:
                generate_report(results, output_format, output_file)
                console.print(f"[green]Report saved to {output_file}[/green]")
            except ValueError as e:
                console.print(f"[red]Failed to generate report: {str(e)}[/red]")
                raise typer.Exit(1)
        else:
            # Print results to console
            for result in results:
                status_color = "\033[92m" if 200 <= result.status_code < 300 else "\033[91m"
                console.print(f"{status_color}{result.method} {result.url} - {result.status_code}\033[0m")
                if result.error:
                    console.print(f"Error: {result.error}")
                if result.response:
                    console.print(f"Response: {result.response}")
                console.print()
                
    except Exception as e:
        console.print(f"[red]Scan failed: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()