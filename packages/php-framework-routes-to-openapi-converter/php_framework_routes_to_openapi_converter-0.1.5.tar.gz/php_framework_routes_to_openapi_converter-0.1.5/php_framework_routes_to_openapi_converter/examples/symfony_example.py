#!/usr/bin/env python3
"""
Symfony Framework Routes to OpenAPI Converter Example.

This file demonstrates how to use the library specifically for Symfony framework.
"""

import json

from php_framework_routes_to_openapi_converter.core import (
    convert_routes_to_openapi,
    get_converter,
    validate_framework,
)


def main():
    print("Symfony Routes to OpenAPI Converter Example")
    print()
    
    # Validate Symfony framework support
    if not validate_framework('symfony'):
        print("Symfony framework not supported")
        return
    
    print("Symfony framework validation passed")
    
    # Symfony route examples - using actual Symfony route structure
    print("=== Preparing Symfony routes ===")
    symfony_routes = {
        # Product API endpoints
        "product_list": {
            "path": "/api/products",
            "method": "GET",
            "name": "product_list",
            "defaults": {"_controller": "App\\Controller\\ProductController:list"}
        },
        "product_show": {
            "path": "/api/products/{id}",
            "method": "GET",
            "name": "product_show",
            "defaults": {"_controller": "App\\Controller\\ProductController:show"}
        },
        "product_create": {
            "path": "/api/products",
            "method": "POST",
            "name": "product_create",
            "defaults": {"_controller": "App\\Controller\\ProductController:create"}
        },
        "product_update": {
            "path": "/api/products/{id}",
            "method": "PUT",
            "name": "product_update",
            "defaults": {"_controller": "App\\Controller\\ProductController:update"}
        },
        "product_delete": {
            "path": "/api/products/{id}",
            "method": "DELETE",
            "name": "product_delete",
            "defaults": {"_controller": "App\\Controller\\ProductController:delete"}
        },
        
        # Category management
        "category_index": {
            "path": "/api/categories",
            "method": "GET",
            "name": "category_index",
            "defaults": {"_controller": "App\\Controller\\CategoryController:index"}
        },
        "category_show": {
            "path": "/api/categories/{slug}",
            "method": "GET",
            "name": "category_show",
            "defaults": {"_controller": "App\\Controller\\CategoryController:show"}
        },
        "category_products": {
            "path": "/api/categories/{id}/products",
            "method": "GET",
            "name": "category_products",
            "defaults": {"_controller": "App\\Controller\\CategoryController:getProducts"}
        },
        
        # User management with Symfony-style routes
        "user_index": {
            "path": "/api/users",
            "method": "GET",
            "name": "user_index",
            "defaults": {"_controller": "App\\Controller\\UserController:index"}
        },
        "user_profile": {
            "path": "/api/users/{id}",
            "method": "GET",
            "name": "user_profile",
            "defaults": {"_controller": "App\\Controller\\UserController:profile"}
        },
        
        # Authentication routes
        "security_login": {
            "path": "/api/login",
            "method": "POST",
            "name": "security_login",
            "defaults": {"_controller": "App\\Controller\\SecurityController:login"}
        },
        "security_logout": {
            "path": "/api/logout",
            "method": "POST",
            "name": "security_logout",
            "defaults": {"_controller": "App\\Controller\\SecurityController:logout"}
        },
        
        # Admin routes with different namespace
        "admin_stats": {
            "path": "/api/admin/stats",
            "method": "GET",
            "name": "admin_stats",
            "defaults": {"_controller": "App\\Controller\\Admin\\StatsController:dashboard"}
        },
        "admin_users": {
            "path": "/api/admin/users",
            "method": "GET",
            "name": "admin_users",
            "defaults": {"_controller": "App\\Controller\\Admin\\UserManagementController:list"}
        },
        
        # Symfony flexible routing with multiple methods
        "search_api_get": {
            "path": "/api/search",
            "method": "GET",
            "name": "search_api_get",
            "defaults": {"_controller": "App\\Controller\\SearchController:search"}
        },
        "search_api_post": {
            "path": "/api/search",
            "method": "POST",
            "name": "search_api_post",
            "defaults": {"_controller": "App\\Controller\\SearchController:search"}
        },
        
        # Example from the comment structure
        "pim_enrich_channel_category_trees_get": {
            "path": "/configuration/channel/category-tree",
            "method": "GET",
            "name": "pim_enrich_channel_category_trees_get",
            "defaults": {"_controller": "pim_enrich.controller.rest.channel:listCategoryTreeAction"},
            "host": "ANY",
            "scheme": "ANY",
            "class": "Symfony\\Component\\Routing\\Route",
            "requirements": "NO CUSTOM",
            "options": {"compiler_class": "Symfony\\Component\\Routing\\RouteCompiler"}
        }
    }
    
    print(f"Symfony routes prepared: {len(symfony_routes)} routes")
    print()
    
    # Convert Symfony routes to OpenAPI
    print("=== Converting Symfony routes to OpenAPI specification ===")
    symfony_spec = convert_routes_to_openapi(
        routes=symfony_routes,
        framework="symfony",
        api_title="Symfony API Documentation", 
        api_version="2.0.0"
    )
    
    print(f"Symfony OpenAPI spec generated:")
    print(f"   - OpenAPI version: {symfony_spec['openapi']}")
    print(f"   - API title: {symfony_spec['info']['title']}")
    print(f"   - API version: {symfony_spec['info']['version']}")
    print(f"   - Paths count: {len(symfony_spec['paths'])}")
    print()
    
    # Analyze specific Symfony route patterns
    print("=== Analyzing Symfony route patterns ===")
    converter = get_converter("symfony")
    
    # Analyze a typical Symfony API route
    api_route = symfony_routes["product_list"]
    print(f"API route analysis:")
    print(f"   - Original path: {api_route['path']}")
    print(f"   - Extracted path: {converter.extract_path(api_route)}")
    print(f"   - Methods: {converter.extract_methods(api_route)}")
    print(f"   - Summary: {converter.extract_summary(api_route)}")
    print(f"   - Tags: {converter.extract_tags(api_route)}")
    print()
    
    # Analyze Symfony parameterized route
    param_route = symfony_routes["category_products"]  # categories/{id}/products
    print(f"Parameterized route analysis:")
    print(f"   - Original path: {param_route['path']}")
    print(f"   - Extracted path: {converter.extract_path(param_route)}")
    print(f"   - Methods: {converter.extract_methods(param_route)}")
    print(f"   - Summary: {converter.extract_summary(param_route)}")
    print(f"   - Tags: {converter.extract_tags(param_route)}")
    print()
    
    # Analyze the example from comment structure
    comment_route = symfony_routes["pim_enrich_channel_category_trees_get"]  # pim_enrich example
    print(f"Comment structure route analysis:")
    print(f"   - Original path: {comment_route['path']}")
    print(f"   - Extracted path: {converter.extract_path(comment_route)}")
    print(f"   - Methods: {converter.extract_methods(comment_route)}")
    print(f"   - Summary: {converter.extract_summary(comment_route)}")
    print(f"   - Tags: {converter.extract_tags(comment_route)}")
    print()
    
    # Show path groupings by controller
    path_groups = {}
    for path_key, path_data in symfony_spec['paths'].items():
        for method, method_data in path_data.items():
            tags = method_data.get('tags', [])
            for tag in tags:
                if tag not in path_groups:
                    path_groups[tag] = []
                path_groups[tag].append(f"{method.upper()} {path_key}")
    
    print("=== Symfony API structure by controller ===")
    for controller, endpoints in path_groups.items():
        print(f"{controller}:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        print()
    
    # Demonstrate route name mapping
    print("=== Symfony route name to path mapping ===")
    for route_name, route_data in symfony_routes.items():
        path = converter.extract_path(route_data)
        print(f"{route_name} → {path}")
    print()
    
    # Save Symfony-specific output
    output_file = "symfony_openapi_spec.json"
    print(f"Saving Symfony OpenAPI specification to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(symfony_spec, f, indent=2, ensure_ascii=False)
    
    print("Symfony example completed successfully!")


if __name__ == "__main__":
    main() 