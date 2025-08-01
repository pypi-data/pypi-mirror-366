"""PHP Framework Routes to OpenAPI Converter.

A Python library and CLI tool for converting PHP framework routes 
to OpenAPI 3.0 specifications.

Supported frameworks:
- Laravel
- Symfony  
- CodeIgniter

Example:
    >>> from php_framework_routes_to_openapi_converter import convert_routes_to_openapi
    >>> routes = [{"uri": "/users", "methods": ["GET"], "name": "users.index"}]
    >>> spec = convert_routes_to_openapi(routes, "laravel")
    >>> print(spec["openapi"])
    3.0.0
"""

from php_framework_routes_to_openapi_converter.core import (
    convert_routes_to_openapi,
    get_converter,
    get_supported_frameworks,
    validate_framework,
)

from php_framework_routes_to_openapi_converter.converters import (
    RouteConverter,
    LaravelConverter,
    SymfonyConverter,
    CodeIgniterConverter,
    CakePHPConverter,
    DrupalConverter,
    DrushConverter,
    FastRouteConverter,
    FatFreeConverter,
    FuelConverter,
    LaminasConverter,
    PhalconConverter,
    PhpixieConverter,
    PopPHPConverter,
    SlimConverter,
    ThinkPHPConverter,
    YiiConverter,
    ZendFrameworkConverter,
)

__version__ = "0.1.0"

__all__ = [
    # Core API functions
    "convert_routes_to_openapi",
    "get_converter", 
    "get_supported_frameworks",
    "validate_framework",
    
    # Converter classes
    "RouteConverter",
    "LaravelConverter",
    "SymfonyConverter", 
    "CodeIgniterConverter",
    "CakePHPConverter",
    "DrupalConverter",
    "DrushConverter",
    "FastRouteConverter",
    "FatFreeConverter",
    "FuelConverter",
    "LaminasConverter",
    "PhalconConverter",
    "PhpixieConverter",
    "PopPHPConverter",
    "SlimConverter",
    "ThinkPHPConverter",
    "YiiConverter",
    "ZendFrameworkConverter",
] 