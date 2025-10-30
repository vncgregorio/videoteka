# Videoteka

A desktop application for downloading YouTube videos with support for parallel downloads, quality settings, and advanced features.

> **New to the project?** Check out the [Quick Start Guide](QUICKSTART.md) to get started in 5 minutes!

## Features

- Download multiple YouTube videos simultaneously
- Configurable video quality and format settings
- Download queue management with pause/resume
- Download history tracking
- Real-time progress monitoring
- Clean PyQt6-based GUI with dark theme

## Installation

### Using Virtual Environment (Recommended)

To avoid conflicts with your system Python installation, it's recommended to use a virtual environment:

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

5. When done, deactivate the virtual environment:
```bash
deactivate
```

### Direct Installation (Not Recommended)

If you prefer to install directly on your system:

```bash
pip install -r requirements.txt
python main.py
```

**Note:** This may conflict with other Python packages on your system.

## Usage

1. Paste YouTube URLs (one per line) or click "Add URLs"
2. Select download folder
3. Configure quality settings (optional)
4. Start downloads
5. Monitor progress in the queue
6. View download history

## Distribution/Building Executables

> **For detailed distribution instructions, see [DISTRIBUTION.md](DISTRIBUTION.md)**

### Quick Build (All Platforms)

Use the provided build script:

```bash
# Make sure you're in your virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Run the build script
python build.py
```

The executable will be in the `dist/` folder as `Videoteka`.

### Windows (.exe)

#### Using the build script (Recommended):
```bash
python build.py
```

#### Manual build with PyInstaller:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --name="Videoteka" --windowed --onefile --icon=icon.ico main.py
```

The executable will be in the `dist/` folder.

### Linux (Flatpak)

To create a Flatpak distribution:

1. Install Flatpak and flatpak-builder:
```bash
# Ubuntu/Debian
sudo apt install flatpak flatpak-builder

# Fedora
sudo dnf install flatpak flatpak-builder

# Arch
sudo pacman -S flatpak flatpak-builder
```

2. Build the Flatpak using the provided manifest:
```bash
flatpak-builder --user --install build-dir org.videoteka.app.yml
flatpak run org.videoteka.app
```

3. To create a distributable Flatpak bundle:
```bash
flatpak-builder --repo=repo build-dir org.videoteka.app.yml
flatpak build-bundle repo videoteka.flatpak org.videoteka.app
```

**Note:** The manifest file `org.videoteka.app.yml` is already included in the project.

### Linux (AppImage)

To create an AppImage distribution:

1. Install build dependencies:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

2. Use the AppImage build script:
```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

3. The AppImage will be created in the current directory as `Videoteka-x86_64.AppImage`

4. Make it executable and run:
```bash
chmod +x Videoteka-x86_64.AppImage
./Videoteka-x86_64.AppImage
```

**Note:** The `build_appimage.sh` script and `AppImageBuilder.yml` are already included in the project.

### macOS (.app/.dmg)

#### Using the build script (Recommended):
```bash
python build.py
```

#### Manual build:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the .app bundle:
```bash
pyinstaller --name="Videoteka" --windowed --onefile --icon=icon.icns main.py
```

3. Create a DMG (optional):
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg --volname "Videoteka" dist/Videoteka.dmg dist/Videoteka.app
```

### Advanced: Custom PyInstaller Build

For advanced customization, you can use the provided spec file template:

```bash
# Copy the template
cp Videoteka.spec.template Videoteka.spec

# Edit Videoteka.spec to customize (add icon, etc.)
# Then build with:
pyinstaller Videoteka.spec

# The executable will be in dist/
```

**Note:** Make sure to add your icon file (`.ico` for Windows, `.icns` for macOS) and update the icon path in the spec file.

**Note:** For all distribution methods, make sure to test the application thoroughly in the target environment before distributing.

## Version Management

Videoteka uses semantic versioning (major.minor.patch) for releases. The version information is centralized in the `version.py` file and can be easily updated using the provided script.

### Updating Version Numbers

To update the version number for a new release:

```bash
# Update to version 1.1.0
python3 update_version.py 1 1 0

# Update to version 2.0.0  
python3 update_version.py 2 0 0

# Update to version 1.0.1
python3 update_version.py 1 0 1
```

The script will automatically update:
- `version.py` with the new version numbers
- `org.videoteka.app.appdata.xml` with release information
- All version references will be consistent across the project

### Version Components

- **Major**: Increment for incompatible API changes or major feature additions
- **Minor**: Increment for backwards-compatible new features
- **Patch**: Increment for backwards-compatible bug fixes

### Git Integration

When you're ready to create a release:

1. Update the version using the script above
2. Commit the changes: `git add . && git commit -m "Bump version to X.Y.Z"`
3. Create a tag: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
4. Push the tag: `git push origin vX.Y.Z`

## License

GPLv3 - See [LICENSE](LICENSE) file for details.


