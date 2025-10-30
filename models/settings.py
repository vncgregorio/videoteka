"""Settings model for application configuration."""
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict


def get_app_data_dir():
    """Get the application data directory for storing user data."""
    # Check if running in AppImage (APPDIR is set)
    if 'APPDIR' in os.environ:
        # Use XDG_CONFIG_HOME or fallback to ~/.config
        config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        app_dir = os.path.join(config_home, 'videoteka')
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    
    # For PyInstaller executable (Windows/macOS/Linux)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform == 'win32':
            # Windows: use AppData/Local
            app_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Videoteka')
        elif sys.platform == 'darwin':
            # macOS: use ~/Library/Application Support
            app_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Videoteka')
        else:
            # Linux: use ~/.local/share
            app_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'videoteka')
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    
    # For regular installation (development), use current directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class Settings:
    """Application settings data class."""
    video_quality: str = "best"  # best, 1080p, 720p, 480p, audio
    preferred_format: str = "mp4"  # mp4, webm, mkv
    audio_quality: str = "best"  # best, 192k, 128k
    download_subtitles: bool = True
    subtitles_language: str = "en"
    max_concurrent_downloads: int = 3
    download_folder: str = ""
    
    @classmethod
    def from_file(cls, filename: str = None) -> "Settings":
        """Load settings from JSON file."""
        if filename is None:
            filename = os.path.join(get_app_data_dir(), "config.json")
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError, KeyError):
                pass
        return cls()
    
    def save(self, filename: str = None):
        """Save settings to JSON file."""
        if filename is None:
            filename = os.path.join(get_app_data_dir(), "config.json")
        
        with open(filename, 'w') as f:
            json.dump(asdict(self), f, indent=4)
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DownloadItem:
    """Download queue item data class."""
    url: str
    title: str = ""
    status: str = "queued"  # queued, downloading, paused, completed, error
    progress: float = 0.0
    speed: str = "0.0 MB/s"
    eta: str = ""
    file_size: str = ""
    output_path: str = ""
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        return cls(**data)

