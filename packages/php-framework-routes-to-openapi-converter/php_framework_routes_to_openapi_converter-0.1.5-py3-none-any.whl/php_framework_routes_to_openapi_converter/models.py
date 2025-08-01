"""Data models for PHP framework routes to OpenAPI conversion."""
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class OpenAPIPathItem:
    """Represents an OpenAPI path item.
    
    Attributes:
        path: The URL path of the endpoint
        methods: List of HTTP methods (GET, POST, etc.)
        summary: Human-readable description of the endpoint
        tags: List of tags for grouping endpoints
        parameters: Optional parameters for the endpoint
        request_body: Optional request body schema
        responses: Optional response definitions
    """
    path: str
    methods: List[str]
    summary: str
    tags: List[str]
    parameters: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    
    def openapi(self) -> Dict[str, Any]:
        """Convert this path item to OpenAPI path item format.
        
        Returns:
            Dict containing the OpenAPI path item structure
        """
        path_item = {}
        
        for method in self.methods:
            method_lower = method.lower()
            operation = {
                "summary": self.summary,
                "tags": self.tags,
                "responses": self.responses or {"200": {"description": "Success"}}
            }
            
            if self.parameters:
                operation["parameters"] = self.parameters
            
            if self.request_body and method_lower in ['post', 'put', 'patch']:
                operation["requestBody"] = self.request_body
            
            path_item[method_lower] = operation
        
        return path_item