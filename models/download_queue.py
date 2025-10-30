"""Download queue data model."""
import json
import os
import sys
from typing import List, Optional
from models.settings import DownloadItem


def get_app_data_dir():
    """Get the application data directory for storing user data."""
    # Check if running in AppImage (APPDIR is set)
    if 'APPDIR' in os.environ:
        # Use XDG_DATA_HOME or fallback to ~/.local/share
        data_home = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        app_dir = os.path.join(data_home, 'videoteka')
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


class DownloadQueue:
    """Manages the download queue."""
    
    def __init__(self, filename: str = None):
        self.items: List[DownloadItem] = []
        if filename is None:
            filename = os.path.join(get_app_data_dir(), "queue.json")
        self.filename = filename
    
    def add(self, item: DownloadItem):
        """Add item to queue."""
        self.items.append(item)
    
    def remove(self, url: str) -> bool:
        """Remove item by URL. Returns True if removed."""
        self.items = [item for item in self.items if item.url != url]
        return len(self.items) == 0
    
    def get_item(self, url: str) -> Optional[DownloadItem]:
        """Get item by URL."""
        for item in self.items:
            if item.url == url:
                return item
        return None
    
    def clear_completed(self):
        """Remove completed items."""
        self.items = [item for item in self.items if item.status != "completed"]
    
    def move_up(self, index: int):
        """Move item up in queue."""
        if index > 0:
            self.items[index], self.items[index - 1] = self.items[index - 1], self.items[index]
    
    def move_down(self, index: int):
        """Move item down in queue."""
        if index < len(self.items) - 1:
            self.items[index], self.items[index + 1] = self.items[index + 1], self.items[index]
    
    def get_queued_items(self) -> List[DownloadItem]:
        """Get items that are queued for download."""
        return [item for item in self.items if item.status == "queued"]
    
    def save(self):
        """Save queue to JSON file."""
        try:
            # Filter out completed items before saving
            items_to_save = [item.to_dict() for item in self.items if item.status != "completed"]
            with open(self.filename, 'w') as f:
                json.dump(items_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving queue: {e}")
    
    def load(self):
        """Load queue from JSON file."""
        if not os.path.exists(self.filename):
            return
        
        try:
            with open(self.filename, 'r') as f:
                items_data = json.load(f)
            
            # Convert back to DownloadItem objects
            self.items = []
            for item_data in items_data:
                item = DownloadItem.from_dict(item_data)
                # Reset status to queued for incomplete downloads
                if item.status in ["downloading", "paused"]:
                    item.status = "queued"
                self.items.append(item)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Error loading queue: {e}")
            self.items = []

