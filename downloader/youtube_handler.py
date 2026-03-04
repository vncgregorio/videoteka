"""YouTube handler using yt-dlp."""
import yt_dlp
import os
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
    
    def _get_js_runtimes_option(self) -> dict:
        """Return js_runtimes option, using bundled Node path when in Flatpak or AppImage."""
        if os.environ.get('FLATPAK_ID'):
            return {'node': {'path': '/app/bin/node'}}
        appdir = os.environ.get('APPDIR')
        if appdir:
            node_path = os.path.join(appdir, 'usr', 'bin', 'node')
            if os.path.isfile(node_path):
                return {'node': {'path': node_path}}
        return {'node': {}}
    
    def _base_ydl_opts(self, cookies_file_path: str = "") -> dict:
        """Return base yt-dlp options shared by get_video_info and download_video (cookies, EJS)."""
        opts = {
            'js_runtimes': self._get_js_runtimes_option(),
            'remote_components': ['ejs:github'],
        }
        if cookies_file_path and os.path.exists(cookies_file_path):
            opts['cookiefile'] = cookies_file_path
        return opts
    
    def get_video_info(self, url: str, cookies_file_path: str = "") -> Optional[dict]:
        """Get video information without downloading."""
        try:
            ydl_opts = {
                **self._base_ydl_opts(cookies_file_path),
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

            ydl_opts = {
                **self._base_ydl_opts(config.get('cookies_file_path', '')),
                'outtmpl': output_template,
                'restrict_filenames': True,
                'quiet': False,
                'no_warnings': False,
                'noprogress': False,
                'format': self._get_format_string(config),
            }
            if config.get('video_quality') != 'audio':
                ydl_opts['merge_output_format'] = config.get('preferred_format', 'mp4')
            if self.progress_hook:
                ydl_opts['progress_hooks'] = [self.progress_hook.progress_hook]
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
        """Build format string with fallback chains so requested format is not required to exist."""
        quality = config.get('video_quality', 'best')
        format_type = config.get('preferred_format', 'mp4')
        exts = ['webm', 'mp4', 'mkv']
        ext_order = [format_type] + [e for e in exts if e != format_type]

        if quality == 'audio':
            # Audio only: prefer m4a then webm, then any
            audio_quality = config.get('audio_quality', 'best')
            if audio_quality == 'best':
                return 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best'
            elif audio_quality == '192k':
                return 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio'
            else:
                return 'bestaudio[abr<=128]/bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio'

        # Video with audio: build video part, audio part, and single-format fallbacks
        height_filter = {
            'best': '',
            '1080p': '[height<=1080]',
            '720p': '[height<=720]',
            '480p': '[height<=480]',
        }
        h = height_filter.get(quality, '')

        video_parts = [f'bestvideo{h}[ext={e}]' for e in ext_order] + [f'bestvideo{h}']
        audio_parts = ['bestaudio[ext=m4a]', 'bestaudio[ext=webm]', 'bestaudio']
        single_parts = [f'best{h}[ext={e}]' for e in ext_order] + ['best']

        video_part = '/'.join(video_parts)
        audio_part = '/'.join(audio_parts)
        single_part = '/'.join(single_parts)

        return f'({video_part})+({audio_part})/{single_part}'

