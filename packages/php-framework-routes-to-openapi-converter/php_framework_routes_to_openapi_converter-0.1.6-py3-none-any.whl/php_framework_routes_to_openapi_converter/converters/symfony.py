"""Symfony framework route converter."""
from typing import Dict, List, Any, Iterable, Optional
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter
from php_framework_routes_to_openapi_converter.models import OpenAPIPathItem
from php_framework_routes_to_openapi_converter.utils.parameter_analyzer import ParameterAnalyzer


class SymfonyConverter(RouteConverter):
    """Symfony framework route converter.
    
    Supports parameter extraction from static analysis data when a parameters file
    is provided. The parameters file should be in JSONL format containing method
    parameter information extracted from Symfony controllers.
    
    Example:
        converter = SymfonyConverter(parameters_file="path/to/parameters.jsonl")
        openapi_spec = converter.convert(routes)
    """
    
    def __init__(self, parameters_file: Optional[str] = None):
        """Initialize Symfony converter with optional parameters file.
        
        Args:
            parameters_file: Path to static analysis parameters file
        """
        self.parameter_analyzer = None
        if parameters_file:
            self.parameter_analyzer = ParameterAnalyzer(parameters_file)
    
    def _path_items_generator(self, routes: Iterable) -> Iterable[OpenAPIPathItem]:
        """Generate path items from Symfony routes."""
        for route_name, route_data in routes.items():
            route_data["name"] = route_name

            path = self._get_path(route_data)
            if not path:
                continue
                
            methods = self._get_methods(route_data)
            summary = self._get_summary(route_data)
            tags = self._get_tags(route_data)
            
            # Get parameters and request body if analyzer is available
            parameters = None
            request_body = None
            
            if self.parameter_analyzer:
                controller = route_data.get("controller")
                if controller:
                    # Extract class and method from controller
                    if '::' in controller:
                        parts = controller.split('::', 1)
                        if len(parts) == 2:
                            class_path, method = parts
                            # Extract class name from full path
                            class_parts = class_path.split('\\')
                            class_name = class_parts[-1]  # Get the last part (class name)
                            method_key = f"{class_name}::{method}"
                            
                            method_params = self.parameter_analyzer.get_parameters_for_method(method_key)
                            if method_params:
                                parameters = self.parameter_analyzer.convert_to_openapi_parameters(method_params)
                                request_body = self.parameter_analyzer.get_request_body_schema(method_params)
            
            yield OpenAPIPathItem(
                path=path,
                methods=methods,
                summary=summary,
                tags=tags,
                parameters=parameters,
                request_body=request_body
            )
    
    def _get_path(self, route: Dict[str, Any]) -> str:
        return route.get("path", "")
    
    def _get_methods(self, route: Dict[str, Any]) -> List[str]:
        return [method.lower() for method in route.get("method", "").split("|") if method.strip()]
    
    def _get_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name", "")
    
    def _get_tags(self, route: Dict[str, Any]) -> List[str]:
        return [route.get("name", "")]
