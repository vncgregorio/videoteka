#!/bin/bash
# Build script for creating an AppImage distribution
# This script creates a portable AppImage that can run on any Linux distribution

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Videoteka AppImage Builder${NC}"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run this script as root${NC}"
   exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    echo "Please install python3: sudo apt install python3 (or equivalent for your distro)"
    exit 1
fi

# Check if appimagetool is installed
if ! command -v appimagetool &> /dev/null; then
    echo -e "${YELLOW}appimagetool not found. Installing...${NC}"
    
    # Download appimagetool
    mkdir -p /tmp/appimage-tools
    cd /tmp/appimage-tools
    
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage || {
        echo -e "${RED}Failed to download appimagetool${NC}"
        exit 1
    }
    
    chmod +x appimagetool-x86_64.AppImage
    sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
    
    cd - > /dev/null
    rm -rf /tmp/appimage-tools
    
    echo -e "${GREEN}appimagetool installed successfully${NC}"
fi

# Create build directory
BUILD_DIR="build_appimage"
APP_DIR="AppDir"

echo "Cleaning previous build..."
rm -rf ${BUILD_DIR} ${APP_DIR}

echo "Setting up Python virtual environment..."
python3 -m venv ${BUILD_DIR}/venv
source ${BUILD_DIR}/venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install PyQt6 yt-dlp > /dev/null

echo "Creating AppDir structure..."
mkdir -p ${APP_DIR}/usr/bin
mkdir -p ${APP_DIR}/usr/share/videoteka
mkdir -p ${APP_DIR}/usr/share/applications
mkdir -p ${APP_DIR}/usr/share/icons/hicolor/256x256/apps

# Copy application files
echo "Copying application files..."
cp -r models ${APP_DIR}/usr/share/videoteka/
cp -r downloader ${APP_DIR}/usr/share/videoteka/
cp -r ui ${APP_DIR}/usr/share/videoteka/
cp -r utils ${APP_DIR}/usr/share/videoteka/
cp main.py ${APP_DIR}/usr/share/videoteka/
cp version.py ${APP_DIR}/usr/share/videoteka/

# Copy Python packages from virtual environment
echo "Copying Python dependencies..."
cp -r ${BUILD_DIR}/venv/lib/python*/site-packages/* ${APP_DIR}/usr/share/videoteka/

# Create launcher script
echo "Creating launcher script..."
cat > ${APP_DIR}/usr/bin/videoteka << 'EOF'
#!/bin/bash
# Videoteka Launcher for AppImage

cd "$(dirname "$0")"
export PYTHONPATH="${APPDIR}/usr/share/videoteka:${PYTHONPATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"

python3 ${APPDIR}/usr/share/videoteka/main.py "$@"
EOF

chmod +x ${APP_DIR}/usr/bin/videoteka

# Create desktop file
echo "Creating desktop file..."
cat > ${APP_DIR}/usr/share/applications/videoteka.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Videoteka
Comment=Download YouTube videos with support for parallel downloads
Exec=videoteka
Icon=videoteka
Terminal=false
Categories=AudioVideo;Video;Network;
Keywords=video;youtube;download;downloader;
EOF

# Copy icon if it exists
echo "Copying icon..."
if [ -f "icon.png" ]; then
    convert icon.png -resize 256x256 ${APP_DIR}/usr/share/icons/hicolor/256x256/apps/videoteka.png 2>/dev/null || \
    python3 -c "from PIL import Image; Image.open('icon.png').resize((256, 256)).save('${APP_DIR}/usr/share/icons/hicolor/256x256/apps/videoteka.png')"
else
    echo "Warning: icon.png not found, creating placeholder"
    python3 create_icon.py
    python3 -c "from PIL import Image; Image.open('icon.png').resize((256, 256)).save('${APP_DIR}/usr/share/icons/hicolor/256x256/apps/videoteka.png')"
fi

# Create AppRun
echo "Creating AppRun..."
cat > ${APP_DIR}/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export APPDIR="${HERE}"
"${HERE}/usr/bin/videoteka" "$@"
EOF

chmod +x ${APP_DIR}/AppRun

# Copy desktop file to AppDir root
cp ${APP_DIR}/usr/share/applications/videoteka.desktop ${APP_DIR}/

# Copy icon to AppDir root
cp ${APP_DIR}/usr/share/icons/hicolor/256x256/apps/videoteka.png ${APP_DIR}/videoteka.png

echo "Building AppImage..."
ARCH=$(uname -m)
OUTPUT_FILE="Videoteka-${ARCH}.AppImage"

appimagetool ${APP_DIR} ${OUTPUT_FILE} || {
    echo -e "${RED}Failed to build AppImage${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}Success! AppImage created: ${OUTPUT_FILE}${NC}"
echo ""
echo "To run the AppImage:"
echo "  chmod +x ${OUTPUT_FILE}"
echo "  ./${OUTPUT_FILE}"
echo ""
echo "Cleaning up build directory..."
rm -rf ${BUILD_DIR} ${APP_DIR}

deactivate

