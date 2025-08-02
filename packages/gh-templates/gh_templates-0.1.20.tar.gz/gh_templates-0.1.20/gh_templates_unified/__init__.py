import sys
import platform

def main():
    try:
        # Try to import the platform-specific package
        system = platform.system()
        machine = platform.machine()
        
        if system == "Linux":
            if machine in ["x86_64", "AMD64"]:
                try:
                    from gh_templates_bin import main as platform_main
                    platform_main()
                except ImportError:
                    print("Error: Platform-specific package not found. Try: pip install gh-templates-linux-x64-glibc")
                    sys.exit(1)
            elif machine in ["aarch64", "arm64"]:
                from gh_templates_bin import main as platform_main
                platform_main()
            else:
                print(f"Unsupported Linux architecture: {machine}")
                sys.exit(1)
        elif system == "Darwin":
            from gh_templates_bin import main as platform_main
            platform_main()
        elif system == "Windows":
            from gh_templates_bin import main as platform_main
            platform_main()
        else:
            print(f"Unsupported platform: {system}-{machine}")
            sys.exit(1)
    except ImportError as e:
        print(f"Error: Could not import platform-specific gh-templates package: {e}")
        print("Please ensure the correct platform-specific package is installed.")
        sys.exit(1)
