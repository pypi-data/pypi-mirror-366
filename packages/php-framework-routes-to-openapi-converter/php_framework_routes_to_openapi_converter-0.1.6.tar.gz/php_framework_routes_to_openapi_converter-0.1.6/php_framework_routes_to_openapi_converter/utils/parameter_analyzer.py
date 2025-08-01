"""Parameter analyzer for static analysis data."""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ParameterAnalyzer:
    """Analyzes static analysis parameter data and converts to OpenAPI format."""
    
    def __init__(self, parameters_file: str):
        """Initialize with path to parameters file.
        
        Args:
            parameters_file: Path to the JSONL file containing parameter analysis
        """
        self.parameters_file = Path(parameters_file)
        self._parameters_cache = None
    
    def load_parameters(self) -> Dict[str, Any]:
        """Load parameters from the JSONL file.
        
        Returns:
            Dictionary mapping controller methods to their parameters
        """
        if self._parameters_cache is not None:
            return self._parameters_cache
        
        parameters = {}
        
        if not self.parameters_file.exists():
            return parameters
        
        with open(self.parameters_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Handle new format: each line is a single parameter
                    if 'name' in data and 'class_name' in data and 'method_name' in data:
                        class_name = data.get('class_name', '')
                        method_name = data.get('method_name', '')
                        
                        if class_name and method_name:
                            # Create method key in format "ClassName::methodName"
                            method_key = f"{class_name}::{method_name}"
                            
                            if method_key not in parameters:
                                parameters[method_key] = {
                                    'file': data.get('file', ''),
                                    'class': class_name,
                                    'method': method_name,
                                    'parameters': {}
                                }
                            
                            # Add parameter to the method
                            param_name = data.get('name', '')
                            if param_name:
                                parameters[method_key]['parameters'][param_name] = {
                                    'name': param_name,
                                    'source': data.get('source', 'input'),
                                    'type': data.get('type', 'string'),
                                    'constraints': data.get('constraints', [])
                                }
                    
                    # Handle old format: grouped by method
                    elif 'file' in data and 'functions' in data:
                        file_path = data.get('file', '')
                        functions = data.get('functions', {})
                        
                        for method_name, method_data in functions.items():
                            # Extract class and method name
                            if '::' in method_name:
                                class_name, method_name_only = method_name.split('::', 1)
                            else:
                                class_name = method_name
                                method_name_only = method_name
                            
                            # Store parameters with full method name as key
                            parameters[method_name] = {
                                'file': file_path,
                                'class': class_name,
                                'method': method_name_only,
                                'parameters': method_data.get('parameters', {})
                            }
                            
                except json.JSONDecodeError:
                    continue
        
        self._parameters_cache = parameters
        return parameters
    
    def get_parameters_for_method(self, method_name: str) -> Dict[str, Any]:
        """Get parameters for a specific method.
        
        Args:
            method_name: Full method name (e.g., 'Controller::method')
            
        Returns:
            Dictionary of parameters for the method
        """
        parameters = self.load_parameters()
        return parameters.get(method_name, {}).get('parameters', {})
    
    def convert_to_openapi_parameters(self, method_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert method parameters to OpenAPI parameter format.
        
        Args:
            method_params: Dictionary of parameters from static analysis
            
        Returns:
            List of OpenAPI parameter objects
        """
        openapi_params = []
        
        for param_name, param_info in method_params.items():
            param_type = param_info.get('type', 'string')
            source = param_info.get('source', 'input')
            
            # Map source to OpenAPI parameter location
            location_map = {
                'route': 'path',
                'query': 'query', 
                'input': 'body',
                'property': 'body',
                'attributes': 'body',
                'request': 'body',
                'get': 'query',
                'post': 'body',
                'headers': 'header'
            }
            
            location = location_map.get(source, 'body')
            
            if location == 'body':
                # Body parameters are handled separately in requestBody
                continue
            
            param_obj = {
                'name': param_name,
                'in': location,
                'required': True,  # Default to required
                'schema': {
                    'type': self._map_php_type_to_openapi(param_type)
                }
            }
            
            # Add description if available
            if 'description' in param_info:
                param_obj['description'] = param_info['description']
            
            openapi_params.append(param_obj)
        
        return openapi_params
    
    def get_request_body_schema(self, method_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate request body schema for body parameters.
        
        Args:
            method_params: Dictionary of parameters from static analysis
            
        Returns:
            OpenAPI request body schema or None if no body parameters
        """
        body_params = {}
        
        for param_name, param_info in method_params.items():
            source = param_info.get('source', 'input')
            
            if source in ['input', 'property', 'attributes', 'request', 'post']:
                param_type = param_info.get('type', 'string')
                body_params[param_name] = {
                    'type': self._map_php_type_to_openapi(param_type),
                    'description': f'Parameter: {param_name}'
                }
        
        if not body_params:
            return None
        
        return {
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': body_params,
                        'required': list(body_params.keys())
                    }
                }
            }
        }
    
    def _map_php_type_to_openapi(self, php_type: str) -> str:
        """Map PHP types to OpenAPI types.
        
        Args:
            php_type: PHP type string
            
        Returns:
            OpenAPI type string
        """
        type_mapping = {
            'string': 'string',
            'int': 'integer',
            'integer': 'integer',
            'float': 'number',
            'double': 'number',
            'bool': 'boolean',
            'boolean': 'boolean',
            'array': 'array',
            'object': 'object'
        }
        
        return type_mapping.get(php_type.lower(), 'string') 