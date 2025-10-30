#!/bin/bash
# Script executed inside the AppImage builder environment

# Variables
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
SITE_PACKAGES=/usr/lib/python${PYTHON_VERSION}/site-packages

# Install PyQt6
python3 -m pip install --target=${SITE_PACKAGES} PyQt6 || {
    echo "Failed to install PyQt6"
    exit 1
}

# Install yt-dlp
python3 -m pip install --target=${SITE_PACKAGES} yt-dlp || {
    echo "Failed to install yt-dlp"
    exit 1
}

# Copy application files
mkdir -p ${APPDIR}/usr/share/videoteka
cp -r models ${APPDIR}/usr/share/videoteka/
cp -r downloader ${APPDIR}/usr/share/videoteka/
cp -r ui ${APPDIR}/usr/share/videoteka/
cp -r utils ${APPDIR}/usr/share/videoteka/
cp main.py ${APPDIR}/usr/share/videoteka/
cp version.py ${APPDIR}/usr/share/videoteka/

# Create launcher script
mkdir -p ${APPDIR}/usr/bin
cat > ${APPDIR}/usr/bin/videoteka << 'EOF'
#!/bin/bash
# Videoteka Launcher for AppImage

# Set up Python path
export PYTHONPATH="${PYTHONPATH}:${APPDIR}/usr/share/videoteka:${PYTHON_SITE_PACKAGES}"

# Run the application
python3 ${APPDIR}/usr/share/videoteka/main.py "$@"
EOF

chmod +x ${APPDIR}/usr/bin/videoteka

# Create desktop file
mkdir -p ${APPDIR}/usr/share/applications
cat > ${APPDIR}/usr/share/applications/videoteka.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Videoteka
Comment=Download YouTube videos with support for parallel downloads and quality settings
Exec=videoteka
Icon=videoteka
Terminal=false
Categories=AudioVideo;Video;Network;
EOF

# Create simple icon (if icon file doesn't exist)
if [ ! -f "${APPDIR}/videoteka.png" ]; then
    mkdir -p ${APPDIR}
    # Create a simple colored square as a placeholder icon
    # In production, you should replace this with an actual icon
    cat > ${APPDIR}/create_icon.py << 'ICONPY'
#!/usr/bin/env python3
from PIL import Image, ImageDraw
img = Image.new('RGB', (512, 512), color=(220, 53, 69))
draw = ImageDraw.Draw(img)
# Draw a play button shape
draw.polygon([(200, 100), (200, 412), (412, 256)], fill=(255, 255, 255))
img.save('videoteka.png')
ICONPY
    python3 ${APPDIR}/create_icon.py 2>/dev/null || echo "Icon creation failed"
    rm ${APPDIR}/create_icon.py
fi

# Copy icon to proper location
if [ -f "${APPDIR}/videoteka.png" ]; then
    mkdir -p ${APPDIR}/usr/share/icons/hicolor/512x512/apps
    cp ${APPDIR}/videoteka.png ${APPDIR}/usr/share/icons/hicolor/512x512/apps/videoteka.png
fi

echo "AppImage build script completed successfully"

