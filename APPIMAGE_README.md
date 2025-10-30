# Creating an AppImage Distribution

This guide explains how to create an AppImage distribution of Videoteka.

## What is an AppImage?

AppImage is a format for packaging software in a way that allows it to run on various Linux distributions without installation. It's similar to portable applications on Windows.

**Advantages:**
- No installation required
- Portable across different Linux distributions
- Self-contained (includes all dependencies)
- Easy to distribute and update

## Building the AppImage

### Quick Start

1. **Make sure you have the required tools:**
   ```bash
   python3 --version  # Should be 3.8+
   ```

2. **Run the build script:**
   ```bash
   chmod +x build_appimage.sh
   ./build_appimage.sh
   ```

3. **That's it!** The AppImage will be created in the current directory as `Videoteka-x86_64.AppImage`

### What the Build Script Does

The `build_appimage.sh` script:

1. **Checks dependencies** - Verifies Python 3 is installed
2. **Downloads appimagetool** - Downloads the AppImage creation tool if not present
3. **Creates virtual environment** - Sets up an isolated Python environment
4. **Installs dependencies** - Installs PyQt6 and yt-dlp
5. **Copies application files** - Copies all necessary files into the AppDir
6. **Creates launcher** - Creates the executable entry point
7. **Creates desktop integration** - Creates .desktop file and icon
8. **Builds AppImage** - Uses appimagetool to create the final AppImage
9. **Cleans up** - Removes temporary build files

### Manual Build (Advanced)

If you need more control or want to understand the process:

1. **Install appimagetool:**
   ```bash
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install PyQt6 yt-dlp
   ```

3. **Create AppDir structure:**
   ```bash
   mkdir -p AppDir/usr/{bin,share/videoteka}
   ```

4. **Copy files:**
   ```bash
   cp -r models downloader ui utils main.py AppDir/usr/share/videoteka/
   cp -r venv/lib/python*/site-packages/* AppDir/usr/share/videoteka/
   ```

5. **Create launcher:**
   ```bash
   cat > AppDir/usr/bin/videoteka << 'EOF'
   #!/bin/bash
   cd "$(dirname "$0")"
   export PYTHONPATH="${APPDIR}/usr/share/videoteka:${PYTHONPATH}"
   python3 ${APPDIR}/usr/share/videoteka/main.py "$@"
   EOF
   chmod +x AppDir/usr/bin/videoteka
   ```

6. **Create AppRun:**
   ```bash
   cat > AppDir/AppRun << 'EOF'
   #!/bin/bash
   HERE="$(dirname "$(readlink -f "${0}")")"
   export APPDIR="${HERE}"
   "${HERE}/usr/bin/videoteka" "$@"
   EOF
   chmod +x AppDir/AppRun
   ```

7. **Create desktop file:**
   ```bash
   cat > AppDir/videoteka.desktop << 'EOF'
   [Desktop Entry]
   Type=Application
   Name=Videoteka
   Exec=videoteka
   Icon=videoteka
   Terminal=false
   Categories=AudioVideo;
   EOF
   ```

8. **Create icon (if you have ImageMagick):**
   ```bash
   convert -size 256x256 xc:'#DC3545' AppDir/videoteka.png
   ```

9. **Build AppImage:**
   ```bash
   appimagetool AppDir Videoteka-x86_64.AppImage
   ```

## Testing the AppImage

1. **Make it executable:**
   ```bash
   chmod +x Videoteka-x86_64.AppImage
   ```

2. **Run it:**
   ```bash
   ./Videoteka-x86_64.AppImage
   ```

3. **Test basic functionality:**
   - Application starts
   - GUI displays correctly
   - Can add URLs to queue
   - Downloads work
   - Settings are saved

## Distribution

### Sharing the AppImage

1. **Upload to a release** - Upload the AppImage to GitHub Releases
2. **Provide instructions** - Tell users to make it executable and run it
3. **Optional: Add to AppImage Hub** - Register on appimage.github.io

### User Instructions

Users can run the AppImage like this:

```bash
# Download the AppImage
wget https://github.com/yourusername/videoteka/releases/download/v1.0.0/Videoteka-x86_64.AppImage

# Make it executable
chmod +x Videoteka-x86_64.AppImage

# Run it
./Videoteka-x86_64.AppImage
```

Users can also:
- Double-click it in file managers (most modern ones)
- Create a launcher for it
- Move it to ~/Applications or similar

## Troubleshooting

### Build Script Fails

**Issue:** Build script fails with permission error
- **Solution:** Don't run as root. The script will prompt for sudo when needed.

**Issue:** Cannot download appimagetool
- **Solution:** Check internet connection. Manually download from GitHub and place in /usr/local/bin.

**Issue:** Virtual environment creation fails
- **Solution:** Install python3-venv: `sudo apt install python3-venv`

### AppImage Doesn't Run

**Issue:** Permission denied
- **Solution:** Make it executable: `chmod +x Videoteka-x86_64.AppImage`

**Issue:** Missing libraries
- **Solution:** AppImage should be self-contained. If this happens, report as a bug.

**Issue:** Python error on startup
- **Solution:** Check that all Python packages were copied correctly during build

### Icon Not Showing

**Issue:** No icon in file manager
- **Solution:** Place icon in the correct location in AppDir structure before building

## File Structure Reference

A completed AppImage contains:

```
Videoteka-x86_64.AppImage (the final file)
  AppRun (executable launcher)
  videoteka.desktop (desktop entry)
  videoteka.png (icon)
  usr/
    bin/
      videoteka (script launcher)
    share/
      videoteka/ (application files)
        models/
        downloader/
        ui/
        utils/
        main.py
        [Python packages]
```

## Customization

### Changing the Icon

1. Create a 256x256 or 512x512 PNG icon
2. Save it as `icon.png`
3. Modify `build_appimage.sh` to copy your icon instead of generating one:
   ```bash
   cp icon.png ${APP_DIR}/videoteka.png
   ```

### Adding Files to the AppImage

Edit `build_appimage.sh` and add files to the AppDir:

```bash
# Example: Add a README
cp README.md ${APP_DIR}/usr/share/videoteka/
```

### Including Additional Data

If your app needs additional data files:

```bash
mkdir -p ${APP_DIR}/usr/share/videoteka/data
cp -r your_data_files ${APP_DIR}/usr/share/videoteka/data
```

## Advanced: AppImage with Update Support

To add update support (optional), you can set up AppImage update information. See [AppImage Update documentation](https://docs.appimage.org/reference/appdir.html#appimage-update-information) for details.

## Security Considerations

- The AppImage is unsigned (update-information is set to "none")
- For distribution, consider signing the AppImage
- Users should verify they trust the source before running

## Size Optimization

The AppImage will be approximately 150-200MB because it includes:
- Python runtime
- PyQt6 (~50MB)
- All dependencies
- Your application

To reduce size:
- Use UPX compression (experimental)
- Remove unused Python packages
- Strip binaries

## See Also

- [AppImage Documentation](https://docs.appimage.org/)
- [AppImageKit GitHub](https://github.com/AppImage/AppImageKit)
- [AppImage Hub](https://appimage.github.io/)

