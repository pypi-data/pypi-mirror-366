"""
GitHub Templates CLI tool - unified installer
This package automatically delegates to the appropriate platform-specific binary.
"""
import sys
import platform
import importlib
import subprocess
import os

def get_platform_package_name():
    """Determine the platform-specific package name."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    if machine in ['x86_64', 'amd64']:
        arch = 'x64'
    elif machine in ['aarch64', 'arm64']:
        arch = 'arm64'
    elif machine in ['i386', 'i686']:
        arch = 'x86'
    else:
        arch = machine
    
    # All platform-specific packages use the same module name
    return 'gh_templates_bin'

def main():
    """Main entry point that delegates to the platform-specific binary."""
    try:
        # Import the platform-specific package
        package_name = get_platform_package_name()
        platform_module = importlib.import_module(package_name)
        
        # Call the main function from the platform-specific package
        if hasattr(platform_module, 'main'):
            platform_module.main()
        else:
            print(f"Error: No main function found in {package_name}")
            sys.exit(1)
            
    except ImportError as e:
        system = platform.system()
        machine = platform.machine()
        print(f"Error: Platform-specific package not found for {system}-{machine}")
        print(f"Import error: {e}")
        print()
        print("This usually means:")
        print("1. Your platform is not supported")
        print("2. The platform-specific package failed to install")
        print()
        print("Supported platforms:")
        print("- Linux x64/ARM64")
        print("- macOS x64/ARM64")
        print("- Windows x64")
        print()
        print("Please report this issue at:")
        print("https://github.com/RafaelJohn9/gh-templates/issues")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error running gh-templates: {e}")
        sys.exit(1)

# Allow direct module execution
if __name__ == '__main__':
    main()
