# Distribution Guide

This guide provides detailed instructions for creating distributable packages of Videoteka for different platforms.

## Prerequisites

### For All Platforms
- Python 3.8 or higher
- Virtual environment (recommended)
- All dependencies installed

### Platform-Specific Requirements

#### Windows
- Windows 7 or higher
- PyInstaller (will be installed by build script)

#### macOS
- macOS 10.13 or higher
- PyInstaller (will be installed by build script)
- Optional: `create-dmg` for DMG creation

#### Linux
- Flatpak and flatpak-builder
- KDE Platform 6.5 runtime

## Quick Start

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller  # For executable builds
   ```
4. Run the build script:
   ```bash
   python build.py
   ```

## Detailed Platform Instructions

### Windows

#### Option 1: Automated Build Script
```bash
python build.py
```

#### Option 2: Manual PyInstaller Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build executable:
   ```bash
   pyinstaller --name="Videoteka" ^
               --windowed ^
               --onefile ^
               --hidden-import=PyQt6 ^
               --hidden-import=PyQt6.QtCore ^
               --hidden-import=PyQt6.QtWidgets ^
               --hidden-import=yt_dlp ^
               main.py
   ```

3. Add icon (optional):
   Create an `icon.ico` file (256x256 or 512x512 recommended) and add:
   ```bash
   --icon=icon.ico
   ```

4. Test the executable:
   ```bash
   dist\Videoteka.exe
   ```

#### Distribution Package
Create a ZIP file with:
- `Videoteka.exe`
- README.txt (optional instructions)
- Any additional documentation

### macOS

#### Option 1: Automated Build Script
```bash
python build.py
```

#### Option 2: Manual Build

1. Build the application bundle:
   ```bash
   pyinstaller --name="Videoteka" \
               --windowed \
               --onefile \
               --macos-create-app-bundle \
               --icon=icon.icns \
               main.py
   ```

2. Create a DMG installer (optional):
   ```bash
   # Install create-dmg
   brew install create-dmg
   
   # Create DMG
   create-dmg --volname "Videoteka" \
              --window-pos 200 120 \
              --window-size 800 400 \
              --icon-size 100 \
              --app-drop-link 600 185 \
              "dist/Videoteka.dmg" \
              "dist/Videoteka.app"
   ```

#### Code Signing (Optional, for App Store)

1. Get Apple Developer certificate
2. Sign the bundle:
   ```bash
   codesign --deep --force --verify --verbose \
            --sign "Developer ID Application: Your Name" \
            dist/Videoteka.app
   ```
3. Verify signature:
   ```bash
   codesign --verify --verbose dist/Videoteka.app
   ```

### Linux

#### Flatpak Distribution

1. Install Flatpak and flatpak-builder:
   ```bash
   # Ubuntu/Debian
   sudo apt install flatpak flatpak-builder
   
   # Fedora
   sudo dnf install flatpak flatpak-builder
   
   # Arch
   sudo pacman -S flatpak flatpak-builder
   ```

2. Add KDE runtime repository:
   ```bash
   flatpak remote-add --if-not-exists kdeapps \
     https://distribute.kde.org/kdeapps.flatpakrepo
   ```

3. Build and install locally:
   ```bash
   flatpak-builder --user --install build-dir org.videoteka.app.yml
   ```

4. Test the application:
   ```bash
   flatpak run org.videoteka.app
   ```

5. Create distributable bundle:
   ```bash
   # Create repository
   flatpak-builder --repo=repo build-dir org.videoteka.app.yml
   
   # Create bundle
   flatpak build-bundle repo videoteka.flatpak org.videoteka.app
   ```

6. Install bundle:
   ```bash
   flatpak install videoteka.flatpak
   ```

#### AppImage (Recommended for Distribution)

AppImage provides a portable Linux application that doesn't require installation.

1. **Prerequisites:**
   ```bash
   # Install Python 3 and pip
   sudo apt install python3 python3-pip
   
   # Install appimagetool (if not already installed)
   # The build script will attempt to install this automatically
   ```

2. **Build the AppImage:**
   ```bash
   # Make the build script executable
   chmod +x build_appimage.sh
   
   # Run the build script
   ./build_appimage.sh
   ```

3. **The script will:**
   - Create a virtual environment
   - Install all dependencies
   - Build the AppImage in the current directory
   - Clean up temporary files

4. **Test the AppImage:**
   ```bash
   chmod +x Videoteka-*.AppImage
   ./Videoteka-*.AppImage
   ```

5. **Distribution:**
   - The AppImage is portable and can be run on any Linux distribution
   - No installation required
   - Just make it executable and run it
   - Users can place it in any directory

**Note:** The AppImage includes all dependencies, so it's larger (~150-200MB) but completely self-contained.

## Customization

### Adding an Icon

1. **Windows (.ico)**: 
   - Use tools like GIMP, ImageMagick, or online converters
   - Create icon with 256x256 and 512x512 sizes
   - Save as `icon.ico`

2. **macOS (.icns)**:
   ```bash
   # Convert PNG to ICNS
   mkdir icon.iconset
   # Add PNG files at different sizes (icon_16x16.png, icon_32x32.png, etc.)
   iconutil -c icns icon.iconset
   ```

3. **Linux**: 
   - Use SVG or PNG (at least 256x256)
   - Place in appropriate directory in Flatpak manifest

### Customizing Build Options

Edit `Videoteka.spec.template` to customize:
- One-file vs one-folder bundle
- Console vs windowed application
- Additional data files
- Hidden imports
- UPX compression

Then copy to `.spec` and build:
```bash
cp Videoteka.spec.template Videoteka.spec
# Edit Videoteka.spec
pyinstaller Videoteka.spec
```

## Testing

Before distribution, always test:

- [ ] Application starts without errors
- [ ] All GUI components work correctly
- [ ] Downloads function properly
- [ ] Settings are saved and loaded
- [ ] History is recorded
- [ ] Progress updates display correctly
- [ ] Error handling works (test with invalid URLs)
- [ ] Application closes cleanly

### Test Cases

1. **Basic Download**: Single video URL
2. **Multiple Downloads**: Multiple URLs in queue
3. **Settings**: Change quality, format, etc.
4. **History**: Verify history tracking
5. **Error Handling**: Invalid URL, network error
6. **File Management**: Download folder selection

## Troubleshooting

### Common Issues

#### "Module not found" error in executable
- Add the module to `--hidden-import` in PyInstaller command
- Or add to spec file's `hiddenimports` list

#### Application crashes on launch
- Build with `--debug=all` to see error messages
- Check console output for errors

#### Large file size
- Use UPX compression: add `--upx-dir=/path/to/upx`
- Exclude unnecessary modules: `--exclude-module=module_name`
- Use one-folder instead of one-file: remove `--onefile`

#### Permission errors (Linux)
- Make sure Flatpak has necessary permissions
- Check `finish-args` in manifest

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Search for the error online
3. Try building in a clean virtual environment
4. Verify all dependencies are installed
5. Check platform-specific requirements

## Distribution Checklist

- [ ] Code is tested and working
- [ ] Version number is updated
- [ ] All dependencies are documented
- [ ] License file is included
- [ ] README is up to date
- [ ] Icons are added and working
- [ ] Application works on target platform
- [ ] Installer/uninstaller works (if applicable)
- [ ] Digital signature added (recommended)

## Versioning

Update the version in:
- `main.py` (application name)
- `org.videoteka.app.appdata.xml` (Flatpak metadata)
- Release notes

## License

Distribute according to the GPLv3 License included in the project.

