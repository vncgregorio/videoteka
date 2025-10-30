"""Download manager for handling parallel downloads."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from models.settings import DownloadItem, Settings
from downloader.youtube_handler import YouTubeHandler, YouTubeProgressHook


class DownloadManager(QObject):
    """Manages parallel downloads with progress tracking."""
    
    # Signals
    download_started = pyqtSignal(str)  # url
    progress_updated = pyqtSignal(str, dict)  # url, progress_info
    download_completed = pyqtSignal(str, str)  # url, filepath
    download_failed = pyqtSignal(str, str)  # url, error_message
    
    def __init__(self, max_workers: int = 3, parent=None):
        super().__init__(parent)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_downloads = {}  # url -> progress_hook
        self.running = False
    
    def download_multiple(self, items: List[DownloadItem], config: Settings):
        """Download multiple videos in parallel."""
        if self.running:
            return
        
        self.running = True
        
        for item in items:
            if item.status != "queued":
                continue
            
            self.executor.submit(self._download_single, item, config)
    
    def _download_single(self, item: DownloadItem, config: Settings):
        """Download a single video."""
        # Create progress hook - must be created in main thread
        progress_hook = YouTubeProgressHook(item.url, self)
        
        # Connect signals before starting download
        progress_hook.progress_updated.connect(
            lambda progress_info, url=item.url: self._on_progress(url, progress_info)
        )
        
        self.active_downloads[item.url] = progress_hook
        
        # Start download
        self.download_started.emit(item.url)
        
        # Run download in this thread
        handler = YouTubeHandler(progress_hook)
        success, result = handler.download_video(item.url, config.download_folder, config.to_dict())
        
        if success:
            self.download_completed.emit(item.url, result)
        else:
            self.download_failed.emit(item.url, result)
        
        # Clean up
        if item.url in self.active_downloads:
            del self.active_downloads[item.url]
    
    def _on_progress(self, url: str, progress_info: dict):
        """Handle progress update."""
        self.progress_updated.emit(url, progress_info)
    
    def _on_complete(self, url: str, filepath: str):
        """Handle download completion."""
        self.download_completed.emit(url, filepath)
    
    def _on_error(self, url: str, error: str):
        """Handle download error."""
        self.download_failed.emit(url, error)
    
    def stop_all(self):
        """Stop all active downloads."""
        self.running = False
        # Note: ThreadPoolExecutor doesn't support cancellation of running tasks
        # This just prevents new downloads from starting

