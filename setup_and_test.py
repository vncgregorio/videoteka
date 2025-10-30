#!/usr/bin/env python3
"""Setup verification script."""
import sys
import subprocess

def check_package(package_name):
    """Check if a package is installed."""
    try:
        __import__(package_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False

def main():
    print("Checking dependencies...")
    print()
    
    all_ok = True
    all_ok &= check_package("PyQt6")
    all_ok &= check_package("yt_dlp")
    
    print()
    
    if all_ok:
        print("All dependencies are installed! You can run the application with:")
        print("  python main.py")
        return 0
    else:
        print("Some dependencies are missing. Please install them with:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

