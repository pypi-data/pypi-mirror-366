#!/usr/bin/env python3
"""Framework-agnostic routes to OpenAPI converter CLI."""
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
import structlog

from php_framework_routes_to_openapi_converter.core import (
    convert_routes_to_openapi,
    get_supported_frameworks,
    validate_framework,
)

# Configure logging first
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Configure structlog for CLI output
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.dev.ConsoleRenderer(colors=False, pad_event=20)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    context_class=dict,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main(
    routes_file: Path = typer.Argument(
        ..., 
        help="Input routes.json file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    framework: str = typer.Argument(
        ..., 
        help="Framework name (laravel, symfony, codeigniter)"
    ),
    output_file: Path = typer.Argument(
        ..., 
        help="Output OpenAPI file"
    ),
    parameters_file: Optional[Path] = typer.Option(
        None,
        "--parameters",
        "-p",
        help="Static analysis parameters file (JSONL format). If provided, enables parameter analysis. If not provided, uses basic conversion.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
):
    """Convert routes.json to OpenAPI specification.
    
    Examples:
        # Basic conversion without parameters
        python -m php_framework_routes_to_openapi_converter.cli routes.json laravel output.json
        
        # Enhanced conversion with parameters file
        python -m php_framework_routes_to_openapi_converter.cli routes.json laravel output.json --parameters parameters.jsonl
    """
    # Validate framework using core API
    if not validate_framework(framework):
        supported = ', '.join(get_supported_frameworks())
        logger.error("Unknown framework", 
                    framework=framework, 
                    supported_frameworks=supported)
        raise typer.Exit(1)
    
    try:
        logger.info("Loading routes", file=str(routes_file))
        with open(routes_file) as f:
            routes = json.load(f)
        logger.info("Routes loaded", count=len(routes), framework=framework)
        
        # Handle parameter analysis
        parameters_path = None
        if parameters_file:
            logger.info("Loading parameters", file=str(parameters_file))
            parameters_path = str(parameters_file)
            logger.info("Parameter analysis enabled")
        else:
            logger.info("Using basic conversion (no parameters)")
        
        logger.info("Converting routes", routes_count=len(routes))
        spec = convert_routes_to_openapi(routes, framework, parameters_path)
        logger.info("OpenAPI specification generated", paths_count=len(spec["paths"]))

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Saving specification", file=str(output_file))
        with open(output_file, 'w') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        
        logger.info("Conversion completed", 
                   output_file=str(output_file),
                   paths_converted=len(spec['paths']))
        
    except FileNotFoundError as e:
        logger.error("File not found", error=str(e), file=str(routes_file))
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format", error=str(e), file=str(routes_file))
        raise typer.Exit(1)
    except ValueError as e:
        logger.error("Validation error", error=str(e))
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Conversion failed", error=str(e))
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(main)
