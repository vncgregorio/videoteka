# Quick Start Guide

Get up and running with Videoteka in 5 minutes.

## Setup

1. **Clone or download the project**
   ```bash
   cd videoteka
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Linux/Mac:
   source venv/bin/activate
   
   # Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## First Steps

1. **Open the application** - You should see the main window

2. **Select a download folder**
   - Click "Browse..." next to the folder path
   - Choose where you want videos saved

3. **Add YouTube URLs**
   - Paste one or more YouTube URLs into the text box (one per line)
   - Example: `https://www.youtube.com/watch?v=VIDEO_ID`
   - Click "Add URLs"

4. **Start downloading**
   - Click "Start Downloads" button
   - Watch the progress bars

5. **View progress**
   - Each download shows:
     - Progress bar
     - Download speed
     - Estimated time remaining
     - File size

6. **Manage downloads**
   - Pause: Click pause button on individual items
   - Remove: Click remove button
   - Pause all: Use the "Pause All" button

## Settings

Access settings via the menu: **File → Settings**

Configure:
- **Video Quality**: Best, 1080p, 720p, 480p, or audio only
- **Format**: MP4, WebM, or MKV
- **Audio Quality**: Best, 192k, or 128k
- **Subtitles**: Enable and select language
- **Concurrent Downloads**: How many videos to download at once (1-10)

## View History

Access download history via: **File → History**

See:
- Previous downloads
- Download dates
- File paths
- Quality settings used

## Tips

- **Multiple URLs**: Add multiple URLs before clicking "Add URLs" for batch processing
- **Quality Settings**: Change settings before adding URLs for best results
- **Queue Management**: Remove completed items with "Clear Completed"
- **Pause/Resume**: Pause downloads anytime, they'll resume when you click Start again

## Troubleshooting

**App won't start?**
- Make sure you activated the virtual environment
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Downloads not working?**
- Check your internet connection
- Verify YouTube URLs are valid
- Make sure download folder is writable

**Errors or crashes?**
- Try running with console visible to see error messages
- Check that yt-dlp is up to date: `pip install --upgrade yt-dlp`

## Need More Help?

- Check the main [README.md](README.md) for detailed documentation
- For building executables, see [DISTRIBUTION.md](DISTRIBUTION.md)
- Verify setup: `python setup_and_test.py`

## Keyboard Shortcuts

- **Ctrl+Q** (or Cmd+Q on Mac): Quit application
- **Tab**: Navigate between elements
- **Enter**: Add URLs or start downloads
- **Esc**: Close dialogs

Enjoy downloading videos! 🎥

