"""Drupal framework route converter."""
from typing import Dict, List, Any, Iterable
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter
from php_framework_routes_to_openapi_converter.models import OpenAPIPathItem


class DrupalConverter(RouteConverter):
    """Drupal framework route converter."""
    def _path_items_generator(self, routes: Iterable) -> Iterable[OpenAPIPathItem]:
        raise NotImplementedError("Drupal route converter not implemented")
    
    def _get_path(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Drupal route converter not implemented")
    
    def _get_methods(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Drupal route converter not implemented")
    
    def _get_summary(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Drupal route converter not implemented")
    
    def _get_tags(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Drupal route converter not implemented")