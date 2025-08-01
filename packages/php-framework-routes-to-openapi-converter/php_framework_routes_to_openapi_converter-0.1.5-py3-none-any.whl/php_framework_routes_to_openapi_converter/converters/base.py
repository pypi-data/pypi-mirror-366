"""Abstract base class for framework-specific route converters."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union, Iterable

from php_framework_routes_to_openapi_converter.models import OpenAPIPathItem


class RouteConverter(ABC):
    """Abstract base class for framework-specific route converters.
    
    Each framework has its own route structure:
    - Laravel: List[Dict[str, Any]] - list of route objects
    - Symfony: Dict[str, Dict[str, Any]] - route name to route object mapping
    - CodeIgniter: List[Dict[str, Any]] - list of route objects
    etc.
    """
    def convert(self, routes: Iterable) -> Dict[str, Any]:
        """Convert routes to OpenAPI paths."""
        paths = {}
        
        # Convert path items to OpenAPI format and group by path
        for path_item in self._path_items_generator(routes):
            if path_item.path not in paths:
                paths[path_item.path] = {}
            
            # Convert path item to OpenAPI format and merge
            openapi_path_item = path_item.openapi()
            paths[path_item.path].update(openapi_path_item)
        
        return {
            "openapi": "3.0.0",
            "info": {"title": "API Specification", "version": "1.0.0"},
            "paths": paths
        }

    @abstractmethod
    def _path_items_generator(self, routes: Iterable) -> Iterable[OpenAPIPathItem]:
        """Generate path items from routes."""
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def _get_path(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def _get_methods(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def _get_summary(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def _get_tags(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Subclasses must implement this method")
