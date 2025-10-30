"""YouTube handler using yt-dlp."""
import yt_dlp
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class YouTubeProgressHook(QObject):
    """Progress hook for yt-dlp downloads."""
    
    progress_updated = pyqtSignal(dict)
    download_complete = pyqtSignal(str, str)  # url, filepath
    error_occurred = pyqtSignal(str, str)  # url, error message
    
    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.downloaded_bytes = 0
        self.total_bytes = 0
    
    def progress_hook(self, d: dict):
        """Hook called by yt-dlp for progress updates."""
        status = d.get('status', 'downloading')
        
        # Only process when actively downloading
        if status != 'downloading':
            return
        
        self.downloaded_bytes = d.get('downloaded_bytes', 0)
        self.total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        
        # Calculate progress percentage
        progress = 0.0
        if self.total_bytes > 0:
            progress = (self.downloaded_bytes / self.total_bytes) * 100
        
        # Get speed and ETA
        speed = d.get('speed')
        if speed is None:
            speed = 0
        
        eta = d.get('eta')
        if eta is None:
            eta = 0
        
        # Emit progress signal
        self.progress_updated.emit({
            'status': status,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
            'progress': progress,
            'speed': speed,
            'eta': eta
        })


class YouTubeHandler:
    """Handles YouTube video downloads using yt-dlp."""
    
    def __init__(self, progress_hook: Optional[YouTubeProgressHook] = None):
        self.progress_hook = progress_hook
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """Get video information without downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                }
        except Exception as e:
            return None
    
    def download_video(self, url: str, output_path: str, config: dict) -> tuple[bool, str]:
        """
        Download a video.
        Returns: (success: bool, file_path: str or error_message: str)
        """
        try:
            # Build output template
            output_template = f"{output_path}/%(title)s.%(ext)s"
            
            # Build yt-dlp options
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'noprogress': False,
                'format': self._get_format_string(config),
            }
            
            # Add progress hook if available
            if self.progress_hook:
                ydl_opts['progress_hooks'] = [self.progress_hook.progress_hook]
            
            # Add subtitle options if enabled
            if config.get('download_subtitles', False):
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = [config.get('subtitles_language', 'en')]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return (True, filename)
                
        except Exception as e:
            return (False, str(e))
    
    def _get_format_string(self, config: dict) -> str:
        """Build format string based on configuration."""
        quality = config.get('video_quality', 'best')
        format_type = config.get('preferred_format', 'mp4')
        
        if quality == 'audio':
            # Audio only
            audio_quality = config.get('audio_quality', 'best')
            if audio_quality == 'best':
                return 'bestaudio/best'
            elif audio_quality == '192k':
                return 'bestaudio[ext=m4a]/bestaudio'
            else:
                return 'bestaudio[abr<=128]/bestaudio'
        
        # Video with audio
        format_map = {
            'best': f'bestvideo[ext={format_type}]+bestaudio[ext=m4a]/best[ext={format_type}]/best',
            '1080p': f'bestvideo[height<=1080][ext={format_type}]+bestaudio[ext=m4a]/best[height<=1080][ext={format_type}]/best',
            '720p': f'bestvideo[height<=720][ext={format_type}]+bestaudio[ext=m4a]/best[height<=720][ext={format_type}]/best',
            '480p': f'bestvideo[height<=480][ext={format_type}]+bestaudio[ext=m4a]/best[height<=480][ext={format_type}]/best',
        }
        
        return format_map.get(quality, format_map['best'])

