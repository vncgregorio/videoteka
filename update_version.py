#!/usr/bin/env python3
"""Script to update version numbers across the project."""

import re
import sys
from pathlib import Path


def update_version_file(major, minor, patch):
    """Update the version.py file with new version numbers."""
    version_file = Path("version.py")
    
    if not version_file.exists():
        print("Error: version.py not found!")
        return False
    
    # Read current content
    content = version_file.read_text()
    
    # Update version numbers
    content = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{major}.{minor}.{patch}"', content)
    content = re.sub(r'__version_info__ = \([^)]*\)', f'__version_info__ = ({major}, {minor}, {patch})', content)
    content = re.sub(r'MAJOR = \d+', f'MAJOR = {major}', content)
    content = re.sub(r'MINOR = \d+', f'MINOR = {minor}', content)
    content = re.sub(r'PATCH = \d+', f'PATCH = {patch}', content)
    
    # Write updated content
    version_file.write_text(content)
    print(f"Updated version.py to {major}.{minor}.{patch}")
    return True


def update_appdata_xml(major, minor, patch):
    """Update the appdata.xml file with new version."""
    appdata_file = Path("org.videoteka.app.appdata.xml")
    
    if not appdata_file.exists():
        print("Warning: org.videoteka.app.appdata.xml not found!")
        return False
    
    content = appdata_file.read_text()
    
    # Update version in appdata.xml (if there's a version field)
    # Note: AppData XML doesn't typically have a version field, but we can add release info
    if '<release version=' not in content:
        # Add release information if not present
        release_info = f'  <releases>\n    <release version="{major}.{minor}.{patch}" date="{__import__("datetime").datetime.now().strftime("%Y-%m-%d")}"/>\n  </releases>\n'
        content = content.replace('  <url type="homepage">', release_info + '  <url type="homepage">')
        appdata_file.write_text(content)
        print(f"Added release info to appdata.xml for {major}.{minor}.{patch}")
    else:
        # Update existing release version
        content = re.sub(r'<release version="[^"]*"', f'<release version="{major}.{minor}.{patch}"', content)
        appdata_file.write_text(content)
        print(f"Updated appdata.xml to {major}.{minor}.{patch}")
    
    return True


def main():
    """Main function to update version numbers."""
    if len(sys.argv) != 4:
        print("Usage: python update_version.py <major> <minor> <patch>")
        print("Example: python update_version.py 1 2 3")
        sys.exit(1)
    
    try:
        major = int(sys.argv[1])
        minor = int(sys.argv[2])
        patch = int(sys.argv[3])
    except ValueError:
        print("Error: Version numbers must be integers")
        sys.exit(1)
    
    print(f"Updating version to {major}.{minor}.{patch}...")
    
    success = True
    success &= update_version_file(major, minor, patch)
    success &= update_appdata_xml(major, minor, patch)
    
    if success:
        print(f"Successfully updated version to {major}.{minor}.{patch}")
    else:
        print("Some updates failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
