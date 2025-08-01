"""Core API for PHP framework routes to OpenAPI conversion."""
from typing import Dict, List, Any, Optional, Union, Iterable

from php_framework_detector.core.models import FrameworkType
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


def get_converter(framework: str, parameters_file: Optional[str] = None) -> RouteConverter:
    """Get the appropriate converter for the framework.
    
    Args:
        framework: The PHP framework name (case-insensitive)
        parameters_file: Optional path to static analysis parameters file
        
    Returns:
        RouteConverter: The appropriate converter instance
        
    Raises:
        ValueError: If the framework is not supported
        
    Example:
        >>> converter = get_converter("laravel")
        >>> isinstance(converter, LaravelConverter)
        True
    """
    converters = {
        FrameworkType.LARAVEL: LaravelConverter(parameters_file),
        FrameworkType.SYMFONY: SymfonyConverter(), 
        FrameworkType.CODEIGNITER: CodeIgniterConverter(),
        FrameworkType.CAKEPHP: CakePHPConverter(),
        FrameworkType.YII: YiiConverter(),
        FrameworkType.THINKPHP: ThinkPHPConverter(),
        FrameworkType.SLIM: SlimConverter(),
        FrameworkType.FATFREE: FatFreeConverter(),
        FrameworkType.FASTROUTE: FastRouteConverter(),
        FrameworkType.FUEL: FuelConverter(),
        FrameworkType.PHALCON: PhalconConverter(),
        FrameworkType.PHPIXIE: PhpixieConverter(),
        FrameworkType.POPPHP: PopPHPConverter(),
        FrameworkType.LAMINAS: LaminasConverter(),
        FrameworkType.ZENDFRAMEWORK: ZendFrameworkConverter(),
        FrameworkType.DRUPAL: DrupalConverter(),
        FrameworkType.DRUSH: DrushConverter(),
    }
    return converters[FrameworkType(framework)] 


def convert_routes_to_openapi(
    routes: Iterable, 
    framework: str, 
    parameters_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert routes to OpenAPI specification using framework-specific converter.
    
    Args:
        routes: Route structure from the framework
            - For Laravel/CodeIgniter: List[Dict[str, Any]]
            - For Symfony: Dict[str, Dict[str, Any]]
        framework: The PHP framework name
        parameters_file: Optional path to static analysis parameters file
        
    Returns:
        Dict containing the complete OpenAPI 3.0 specification
        
    Raises:
        ValueError: If the framework is not supported
        
    Example:
        >>> routes = [{"uri": "/users", "methods": ["GET"], "name": "users.index"}]
        >>> spec = convert_routes_to_openapi(routes, "laravel")
        >>> spec["openapi"]
        '3.0.0'
    """
    return get_converter(framework, parameters_file).convert(routes)


def get_supported_frameworks() -> List[str]:
    """Get list of supported PHP frameworks.
    
    Returns:
        List of supported framework names in lowercase
        
    Example:
        >>> frameworks = get_supported_frameworks()
        >>> "laravel" in frameworks
        True
    """
    return ["laravel", "symfony", "codeigniter"]


def validate_framework(framework: str) -> bool:
    """Validate if a framework is supported.
    
    Args:
        framework: The framework name to validate
        
    Returns:
        True if the framework is supported, False otherwise
        
    Example:
        >>> validate_framework("laravel")
        True
        >>> validate_framework("unknown")
        False
    """
    return framework.lower() in get_supported_frameworks() 