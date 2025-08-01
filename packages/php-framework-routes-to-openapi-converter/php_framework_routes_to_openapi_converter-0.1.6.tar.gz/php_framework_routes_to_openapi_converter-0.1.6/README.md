# PHP Framework Routes to OpenAPI Converter

Convert PHP framework routes to OpenAPI 3.0 specifications.

## Supported Frameworks

- Laravel
- Symfony  
- CodeIgniter

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
python -m php_framework_routes_to_openapi_converter.cli convert routes.json laravel openapi.json
```

Arguments:
1. `routes.json` - Input routes file
2. `laravel` - Framework name (laravel, symfony, codeigniter)
3. `openapi.json` - Output OpenAPI file

### Python

```python
from php_framework_routes_to_openapi_converter import convert_routes_to_openapi

routes = [
    {"uri": "/users", "methods": ["GET"], "name": "users.index"},
    {"uri": "/users/{id}", "methods": ["GET"], "name": "users.show"},
]

spec = convert_routes_to_openapi(routes, "laravel")
```

## Example

```bash
python example.py
```
