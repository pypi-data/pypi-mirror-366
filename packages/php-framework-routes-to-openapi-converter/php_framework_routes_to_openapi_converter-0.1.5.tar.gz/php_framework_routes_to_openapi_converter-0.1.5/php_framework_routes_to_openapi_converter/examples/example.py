#!/usr/bin/env python3
"""
PHP Framework Routes to OpenAPI Converter - Main Example.

This file demonstrates the basic usage of the library and provides
information about framework-specific examples.
"""

import sys
from php_framework_routes_to_openapi_converter import (
    get_supported_frameworks,
    validate_framework,
)


def show_framework_examples():
    """Display information about framework-specific examples."""
    print("\n=== Framework-specific examples available ===")
    
    examples = {
        "laravel": {
            "file": "laravel_example.py",
            "description": "Laravel framework routes with typical Laravel patterns (uri, methods, name, action)"
        },
        "symfony": {
            "file": "symfony_example.py", 
            "description": "Symfony framework routes with path, methods, name, controller structure"
        },
        "codeigniter": {
            "file": "codeigniter_example.py",
            "description": "CodeIgniter framework routes with route, method, controller patterns"
        }
    }
    
    for framework, info in examples.items():
        print(f"📁 {framework.upper()}")
        print(f"   File: {info['file']}")
        print(f"   Description: {info['description']}")
        print()


def main():
    print("🚀 PHP Framework Routes to OpenAPI Converter")
    print()
    
    # Show supported frameworks
    print("=== Getting supported frameworks ===")
    frameworks = get_supported_frameworks()
    print(f"Supported frameworks: {', '.join(frameworks)}")
    print()
    
    # Validate each framework
    print("=== Framework validation ===")
    for framework in frameworks:
        is_supported = validate_framework(framework)
        status = "✅ Supported" if is_supported else "❌ Not supported"
        print(f"{framework}: {status}")
    print()
    
    # Show available examples
    show_framework_examples()
    
    # Usage instructions
    print("=== Usage instructions ===")
    print("Run framework-specific examples:")
    for framework in frameworks:
        print(f"  python examples/{framework}_example.py")
    print()
    
    # Check if user wants to run a specific example
    if len(sys.argv) > 1:
        framework = sys.argv[1].lower()
        if framework in frameworks:
            print(f"🔄 Running {framework} framework example...")
            print()
            try:
                if framework == "laravel":
                    from laravel_example import main as laravel_main
                    laravel_main()
                elif framework == "symfony":
                    from symfony_example import main as symfony_main
                    symfony_main()
                elif framework == "codeigniter":
                    from codeigniter_example import main as codeigniter_main
                    codeigniter_main()
            except ImportError as e:
                print(f"❌ Could not import {framework} example: {e}")
        else:
            print(f"❌ Unsupported framework: {framework}")
            print(f"   Supported frameworks: {', '.join(frameworks)}")
    else:
        print("💡 To run a specific framework example, use:")
        print("   python example.py <framework>")
        print(f"   Available frameworks: {', '.join(frameworks)}")


if __name__ == "__main__":
    main() 