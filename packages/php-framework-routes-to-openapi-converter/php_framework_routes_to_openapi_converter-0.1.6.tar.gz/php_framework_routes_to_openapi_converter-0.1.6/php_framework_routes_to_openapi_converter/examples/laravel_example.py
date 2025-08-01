#!/usr/bin/env python3
"""
Laravel Framework Routes to OpenAPI Converter Example.

This file demonstrates how to use the library specifically for Laravel framework.
"""

import json
from php_framework_routes_to_openapi_converter import (
    convert_routes_to_openapi,
    get_converter,
    validate_framework,
)


def main():
    print("🐘 Laravel Routes to OpenAPI Converter Example")
    print()
    
    # Validate Laravel framework support
    if not validate_framework('laravel'):
        print("❌ Laravel framework not supported")
        return
    
    print("✅ Laravel framework validation passed")
    
    # Laravel route examples - using Laravel's typical route structure
    print("=== Preparing Laravel routes ===")
    
    laravel_routes = [
        # API Resource routes
        {
            "uri": "api/users",
            "method": "|".join(["GET"]),
            "name": "users.index",
            "action": "App\\Http\\Controllers\\UserController@index"
        },
        {
            "uri": "api/users/{id}",
            "method": "|".join(["GET"]),
            "name": "users.show", 
            "action": "App\\Http\\Controllers\\UserController@show"
        },
        {
            "uri": "api/users",
            "method": "|".join(["POST"]),
            "name": "users.store",
            "action": "App\\Http\\Controllers\\UserController@store"
        },
        {
            "uri": "api/users/{id}",
            "method": "|".join(["PUT", "PATCH"]),
            "name": "users.update",
            "action": "App\\Http\\Controllers\\UserController@update"
        },
        {
            "uri": "api/users/{id}",
            "method": "|".join(["DELETE"]),
            "name": "users.destroy",
            "action": "App\\Http\\Controllers\\UserController@destroy"
        },
        
        # Additional API endpoints
        {
            "uri": "api/posts",
            "method": "|".join(["GET"]),
            "name": "posts.index",
            "action": "App\\Http\\Controllers\\PostController@index"
        },
        {
            "uri": "api/posts/{post}",
            "method": "|".join(["GET"]),
            "name": "posts.show",
            "action": "App\\Http\\Controllers\\PostController@show"
        },
        {
            "uri": "api/posts/{post}/comments",
            "method": "|".join(["GET"]),
            "name": "posts.comments.index",
            "action": "App\\Http\\Controllers\\CommentController@index"
        },
        
        # Auth routes
        {
            "uri": "api/auth/login",
            "method": "|".join(["POST"]),
            "name": "auth.login",
            "action": "App\\Http\\Controllers\\Auth\\AuthController@login"
        },
        {
            "uri": "api/auth/logout",
            "method": "|".join(["POST"]),
            "name": "auth.logout",
            "action": "App\\Http\\Controllers\\Auth\\AuthController@logout"
        },
        
        # Admin routes with middleware
        {
            "uri": "api/admin/dashboard",
            "method": "|".join(["GET"]),
            "name": "admin.dashboard",
            "action": "App\\Http\\Controllers\\Admin\\DashboardController@index"
        }
    ]
    
    print(f"📋 Laravel routes prepared: {len(laravel_routes)} routes")
    print()
    
    # Convert Laravel routes to OpenAPI
    print("=== Converting Laravel routes to OpenAPI specification ===")
    laravel_spec = convert_routes_to_openapi(
        routes=laravel_routes,
        framework="laravel",
        api_title="Laravel API Documentation",
        api_version="1.0.0"
    )
    
    print(f"✅ Laravel OpenAPI spec generated:")
    print(f"   - OpenAPI version: {laravel_spec['openapi']}")
    print(f"   - API title: {laravel_spec['info']['title']}")
    print(f"   - API version: {laravel_spec['info']['version']}")
    print(f"   - Paths count: {len(laravel_spec['paths'])}")
    print()
    
    # Analyze specific Laravel route patterns
    print("=== Analyzing Laravel route patterns ===")
    converter = get_converter("laravel")
    
    # Analyze a typical Laravel resource route
    resource_route = laravel_routes[0]
    print(f"📝 Resource route analysis:")
    print(f"   - Original URI: {resource_route['uri']}")
    print(f"   - Extracted path: {converter.extract_path(resource_route)}")
    print(f"   - Methods: {converter.extract_methods(resource_route)}")
    print(f"   - Summary: {converter.extract_summary(resource_route)}")
    print(f"   - Tags: {converter.extract_tags(resource_route)}")
    print()
    
    # Analyze Laravel nested route
    nested_route = laravel_routes[7]  # posts/{post}/comments
    print(f"🔗 Nested route analysis:")
    print(f"   - Original URI: {nested_route['uri']}")
    print(f"   - Extracted path: {converter.extract_path(nested_route)}")
    print(f"   - Methods: {converter.extract_methods(nested_route)}")
    print(f"   - Summary: {converter.extract_summary(nested_route)}")
    print(f"   - Tags: {converter.extract_tags(nested_route)}")
    print()
    
    # Show path groupings by controller
    path_groups = {}
    for path_key, path_data in laravel_spec['paths'].items():
        for method, method_data in path_data.items():
            tags = method_data.get('tags', [])
            for tag in tags:
                if tag not in path_groups:
                    path_groups[tag] = []
                path_groups[tag].append(f"{method.upper()} {path_key}")
    
    print("=== Laravel API structure by controller ===")
    for controller, endpoints in path_groups.items():
        print(f"📂 {controller}:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        print()
    
    # Save Laravel-specific output
    output_file = "laravel_openapi_spec.json"
    print(f"💾 Saving Laravel OpenAPI specification to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(laravel_spec, f, indent=2, ensure_ascii=False)
    
    print("🎉 Laravel example completed successfully!")


if __name__ == "__main__":
    main() 