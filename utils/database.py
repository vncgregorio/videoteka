"""Database utilities for download history."""
import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime


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


class DownloadHistory:
    """Manages download history in SQLite database."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(get_app_data_dir(), "downloads.db")
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                download_date TEXT NOT NULL,
                file_path TEXT,
                file_size TEXT,
                video_quality TEXT,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_download(self, url: str, title: str, file_path: str, 
                     file_size: str, video_quality: str, status: str = "completed"):
        """Add a download to history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO downloads (url, title, download_date, file_path, file_size, video_quality, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (url, title, datetime.now().isoformat(), file_path, file_size, video_quality, status))
        
        conn.commit()
        conn.close()
    
    def get_all_downloads(self, limit: int = 100) -> List[dict]:
        """Get all downloads from history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, title, download_date, file_path, file_size, video_quality, status
            FROM downloads
            ORDER BY download_date DESC
            LIMIT ?
        """, (limit,))
        
        columns = ['id', 'url', 'title', 'download_date', 'file_path', 'file_size', 'video_quality', 'status']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def delete_download(self, download_id: int):
        """Delete a download from history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
        
        conn.commit()
        conn.close()
    
    def clear_history(self):
        """Clear all download history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM downloads")
        
        conn.commit()
        conn.close()

