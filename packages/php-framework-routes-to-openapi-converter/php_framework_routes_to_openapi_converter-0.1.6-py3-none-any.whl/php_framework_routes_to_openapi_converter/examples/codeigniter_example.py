#!/usr/bin/env python3
"""
CodeIgniter Framework Routes to OpenAPI Converter Example.

This file demonstrates how to use the library specifically for CodeIgniter framework.
"""

import json
from php_framework_routes_to_openapi_converter import (
    convert_routes_to_openapi,
    get_converter,
    validate_framework,
)


def main():
    print("🔥 CodeIgniter Routes to OpenAPI Converter Example")
    print()
    
    # Validate CodeIgniter framework support
    if not validate_framework('codeigniter'):
        print("❌ CodeIgniter framework not supported")
        return
    
    print("✅ CodeIgniter framework validation passed")
    
    # CodeIgniter route examples - using CodeIgniter's typical route structure
    print("=== Preparing CodeIgniter routes ===")
    codeigniter_routes = [
        # Basic API routes
        {
            "route": "/api/products",
            "method": "GET",
            "controller": "ProductController::index"
        },
        {
            "route": "/api/products/(:num)",
            "method": "GET", 
            "controller": "ProductController::show"
        },
        {
            "route": "/api/products",
            "method": "POST",
            "controller": "ProductController::create"
        },
        {
            "route": "/api/products/(:num)",
            "method": ["PUT", "PATCH"],
            "controller": "ProductController::update"
        },
        {
            "route": "/api/products/(:num)",
            "method": "DELETE",
            "controller": "ProductController::delete"
        },
        
        # User management routes
        {
            "route": "/api/users",
            "method": "GET",
            "controller": "UserController::index"
        },
        {
            "route": "/api/users/(:num)",
            "method": "GET",
            "controller": "UserController::show"
        },
        {
            "route": "/api/users/profile/(:num)",
            "method": "GET",
            "controller": "UserController::profile"
        },
        
        # Authentication endpoints
        {
            "route": "/api/auth/login",
            "method": "POST",
            "controller": "AuthController::login"
        },
        {
            "route": "/api/auth/logout",
            "method": "POST",
            "controller": "AuthController::logout"
        },
        {
            "route": "/api/auth/register",
            "method": "POST",
            "controller": "AuthController::register"
        },
        
        # Category routes with CodeIgniter patterns
        {
            "route": "/api/categories",
            "method": "GET",
            "controller": "CategoryController::list"
        },
        {
            "route": "/api/categories/(:any)",
            "method": "GET",
            "controller": "CategoryController::show"
        },
        {
            "route": "/api/categories/(:any)/products",
            "method": "GET",
            "controller": "CategoryController::products"
        },
        
        # Search and filtering
        {
            "route": "/api/search",
            "method": ["GET", "POST"],
            "controller": "SearchController::search"
        },
        {
            "route": "/api/search/(:any)",
            "method": "GET",
            "controller": "SearchController::query"
        },
        
        # File upload routes
        {
            "route": "/api/upload/image",
            "method": "POST",
            "controller": "UploadController::image"
        },
        {
            "route": "/api/upload/document",
            "method": "POST",
            "controller": "UploadController::document"
        },
        
        # Admin routes with different structure
        {
            "route": "/api/admin/dashboard",
            "method": "GET",
            "controller": "Admin\\DashboardController::index"
        },
        {
            "route": "/api/admin/users/(:num)/status",
            "method": "PATCH",
            "controller": "Admin\\UserController::updateStatus"
        }
    ]
    
    print(f"📋 CodeIgniter routes prepared: {len(codeigniter_routes)} routes")
    print()
    
    # Convert CodeIgniter routes to OpenAPI
    print("=== Converting CodeIgniter routes to OpenAPI specification ===")
    codeigniter_spec = convert_routes_to_openapi(
        routes=codeigniter_routes,
        framework="codeigniter",
        api_title="CodeIgniter API Documentation",
        api_version="3.0.0"
    )
    
    print(f"✅ CodeIgniter OpenAPI spec generated:")
    print(f"   - OpenAPI version: {codeigniter_spec['openapi']}")
    print(f"   - API title: {codeigniter_spec['info']['title']}")
    print(f"   - API version: {codeigniter_spec['info']['version']}")
    print(f"   - Paths count: {len(codeigniter_spec['paths'])}")
    print()
    
    # Analyze specific CodeIgniter route patterns
    print("=== Analyzing CodeIgniter route patterns ===")
    converter = get_converter("codeigniter")
    
    # Analyze a basic CodeIgniter route
    basic_route = codeigniter_routes[0]
    print(f"📝 Basic route analysis:")
    print(f"   - Original route: {basic_route['route']}")
    print(f"   - Extracted path: {converter.extract_path(basic_route)}")
    print(f"   - Methods: {converter.extract_methods(basic_route)}")
    print(f"   - Summary: {converter.extract_summary(basic_route)}")
    print(f"   - Tags: {converter.extract_tags(basic_route)}")
    print()
    
    # Analyze CodeIgniter parameterized route with (:num)
    param_route = codeigniter_routes[1]  # /api/products/(:num)
    print(f"🔢 Parameterized route analysis (:num):")
    print(f"   - Original route: {param_route['route']}")
    print(f"   - Extracted path: {converter.extract_path(param_route)}")
    print(f"   - Methods: {converter.extract_methods(param_route)}")
    print(f"   - Summary: {converter.extract_summary(param_route)}")
    print(f"   - Tags: {converter.extract_tags(param_route)}")
    print()
    
    # Analyze CodeIgniter route with (:any) parameter
    any_param_route = codeigniter_routes[12]  # /api/categories/(:any)
    print(f"🔤 Any parameter route analysis (:any):")
    print(f"   - Original route: {any_param_route['route']}")
    print(f"   - Extracted path: {converter.extract_path(any_param_route)}")
    print(f"   - Methods: {converter.extract_methods(any_param_route)}")
    print(f"   - Summary: {converter.extract_summary(any_param_route)}")
    print(f"   - Tags: {converter.extract_tags(any_param_route)}")
    print()
    
    # Analyze multi-method route
    multi_method_route = codeigniter_routes[14]  # search with GET,POST
    print(f"🔄 Multi-method route analysis:")
    print(f"   - Original route: {multi_method_route['route']}")
    print(f"   - Extracted path: {converter.extract_path(multi_method_route)}")
    print(f"   - Methods: {converter.extract_methods(multi_method_route)}")
    print(f"   - Summary: {converter.extract_summary(multi_method_route)}")
    print(f"   - Tags: {converter.extract_tags(multi_method_route)}")
    print()
    
    # Show path groupings by controller
    path_groups = {}
    for path_key, path_data in codeigniter_spec['paths'].items():
        for method, method_data in path_data.items():
            tags = method_data.get('tags', [])
            for tag in tags:
                if tag not in path_groups:
                    path_groups[tag] = []
                path_groups[tag].append(f"{method.upper()} {path_key}")
    
    print("=== CodeIgniter API structure by controller ===")
    for controller, endpoints in path_groups.items():
        print(f"📂 {controller}:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        print()
    
    # Demonstrate CodeIgniter route patterns
    print("=== CodeIgniter route pattern analysis ===")
    route_patterns = {}
    for route in codeigniter_routes:
        route_str = route.get('route', '')
        if '(:num)' in route_str:
            route_patterns.setdefault('numeric_params', []).append(route_str)
        elif '(:any)' in route_str:
            route_patterns.setdefault('any_params', []).append(route_str)
        else:
            route_patterns.setdefault('static', []).append(route_str)
    
    for pattern_type, routes in route_patterns.items():
        print(f"🏷️  {pattern_type}: {len(routes)} routes")
        for i, route in enumerate(routes[:3]):  # Show first 3 examples
            print(f"   - {route}")
        if len(routes) > 3:
            print(f"   ... and {len(routes) - 3} more")
        print()
    
    # Save CodeIgniter-specific output
    output_file = "codeigniter_openapi_spec.json"
    print(f"💾 Saving CodeIgniter OpenAPI specification to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(codeigniter_spec, f, indent=2, ensure_ascii=False)
    
    print("🎉 CodeIgniter example completed successfully!")


if __name__ == "__main__":
    main() 