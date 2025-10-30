#!/usr/bin/env python3
"""Build script for creating distributable packages."""
import sys
import subprocess
import platform
import os

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Step: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*50}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"Error: {description} failed with exit code {result.returncode}")
        return False
    return True

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("Installing PyInstaller...")
        return run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                          "Installing PyInstaller")

def build_executable():
    """Build executable based on platform."""
    system = platform.system()
    
    if not check_pyinstaller():
        print("Failed to install PyInstaller. Aborting.")
        return False
    
    base_cmd = ['pyinstaller', '--name=Videoteka', '--onefile', '--windowed']
    
    # Add hidden imports
    hidden_imports = [
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=yt_dlp',
        '--hidden-import=models',
        '--hidden-import=downloader',
        '--hidden-import=ui',
        '--hidden-import=utils',
        '--hidden-import=version',
    ]
    base_cmd.extend(hidden_imports)
    
    # Platform-specific adjustments
    if system == 'Windows':
        print("Building Windows executable...")
        # Windows-specific options if needed
        pass
    elif system == 'Darwin':  # macOS
        print("Building macOS application bundle...")
        base_cmd.append('--macos-create-app-bundle')
    elif system == 'Linux':
        print("Building Linux executable...")
        # Linux-specific options if needed
        pass
    else:
        print(f"Unknown platform: {system}")
        return False
    
    # Add main script
    base_cmd.append('main.py')
    
    return run_command(base_cmd, "Building executable")

def main():
    """Main build function."""
    print("Videoteka - Build Script")
    print("Platform:", platform.system())
    print("Python version:", platform.python_version())
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("\n⚠️  Warning: Not running in a virtual environment!")
        print("It's recommended to build in a clean virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    
    if build_executable():
        print("\n" + "="*50)
        print("✓ Build successful!")
        print("="*50)
        print("\nExecutable location: dist/Videoteka")
        if platform.system() == 'Darwin':
            print("(or dist/Videoteka.app on macOS)")
        print("\nTo test the application, run:")
        if platform.system() == 'Windows':
            print("  dist\\Videoteka.exe")
        elif platform.system() == 'Darwin':
            print("  open dist/Videoteka.app")
        else:
            print("  ./dist/Videoteka")
        return 0
    else:
        print("\n" + "="*50)
        print("✗ Build failed!")
        print("="*50)
        return 1

if __name__ == '__main__':
    sys.exit(main())

