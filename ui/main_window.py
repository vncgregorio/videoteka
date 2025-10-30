"""Main window for the YouTube downloader application."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QFileDialog,
    QScrollArea, QMessageBox, QMenuBar, QStatusBar, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QCloseEvent
from models.settings import Settings, DownloadItem
from models.download_queue import DownloadQueue
from downloader.download_manager import DownloadManager
from downloader.youtube_handler import YouTubeHandler
from ui.settings_dialog import SettingsDialog
from ui.history_dialog import HistoryDialog
from ui.download_item_widget import DownloadItemWidget
from utils.database import DownloadHistory


class VideoInfoWorker(QObject):
    """Worker thread for fetching video information."""
    video_info_fetched = pyqtSignal(str, str)  # url, title
    progress_updated = pyqtSignal(int, int)  # current, total
    all_info_fetched = pyqtSignal(list)  # list of (url, title) tuples
    finished = pyqtSignal()
    
    def __init__(self, urls: list):
        super().__init__()
        self.urls = urls
    
    def fetch_all_info(self):
        """Fetch video information for all URLs."""
        handler = YouTubeHandler()
        results = []
        
        for index, url in enumerate(self.urls):
            info = handler.get_video_info(url)
            title = info.get('title', 'Unknown Video') if info else "Unknown Video"
            results.append((url, title))
            
            # Emit progress update
            self.progress_updated.emit(index + 1, len(self.urls))
        
        self.all_info_fetched.emit(results)
        self.finished.emit()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings.from_file()
        self.download_queue = DownloadQueue()
        self.history = DownloadHistory()
        self.download_manager = DownloadManager(self.settings.max_concurrent_downloads)
        self.info_thread = None
        self.info_worker = None
        
        # Connect download manager signals
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.progress_updated.connect(self.on_progress_updated)
        self.download_manager.download_completed.connect(self.on_download_completed)
        self.download_manager.download_failed.connect(self.on_download_failed)
        
        self.init_ui()
        self.setup_menu_bar()
        
        # Load saved queue on startup
        self.download_queue.load()
        if self.download_queue.items:
            self.update_queue_display()
            self.update_stats()
            self.statusBar.showMessage(f"Loaded {len(self.download_queue.items)} item(s) from previous session")
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Videoteka - Video Downloader")
        self.setMinimumSize(900, 750)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                border: 2px solid #444;
                border-radius: 4px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 12px;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666;
            }
            QStatusBar {
                background-color: #252526;
                border-top: 1px solid #444;
                color: #ffffff;
            }
            QScrollArea {
                background-color: #252526;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #252526;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #3c3c3c;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #252526;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background-color: #3c3c3c;
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #4a4a4a;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #444;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3c3c3c;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # URL Input Section
        url_layout = QVBoxLayout()
        url_label = QLabel("YouTube URLs (one per line):")
        url_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        url_layout.addWidget(url_label)
        
        self.url_text_edit = QTextEdit()
        self.url_text_edit.setPlaceholderText("Paste YouTube URLs here, one per line...")
        self.url_text_edit.setMaximumHeight(100)
        url_layout.addWidget(self.url_text_edit)
        
        self.add_urls_button = QPushButton("Add URLs")
        self.add_urls_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #2d5a2e;
                color: #999;
            }
        """)
        self.add_urls_button.clicked.connect(self.add_urls)
        url_layout.addWidget(self.add_urls_button)
        
        main_layout.addLayout(url_layout)
        
        # Download Folder Section
        folder_layout = QVBoxLayout()
        folder_label = QLabel("Download Folder:")
        folder_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        folder_layout.addWidget(folder_label)
        
        folder_row = QHBoxLayout()
        self.folder_path_label = QLabel(self.settings.download_folder or "No folder selected")
        self.folder_path_label.setStyleSheet("padding: 8px; background-color: #2d2d2d; color: #ffffff; border-radius: 4px;")
        folder_row.addWidget(self.folder_path_label, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_row.addWidget(self.browse_button)
        
        folder_layout.addLayout(folder_row)
        main_layout.addLayout(folder_layout)
        
        # Queue Section
        queue_label = QLabel("Download Queue:")
        queue_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        main_layout.addWidget(queue_label)
        
        # Stats Section
        stats_container = QWidget()
        stats_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(10, 8, 10, 8)
        stats_layout.setSpacing(20)
        
        # Create stat items with color coding
        self.total_label = QLabel("Total: 0")
        self.downloading_label = QLabel("Downloading: 0")
        self.completed_label = QLabel("Completed: 0")
        self.remaining_label = QLabel("Remaining: 0")
        
        # Style stat labels with different colors
        base_style = """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 100px;
                text-align: center;
            }
        """
        
        self.total_label.setStyleSheet(base_style + "QLabel { background-color: #3c3c3c; }")
        self.downloading_label.setStyleSheet(base_style + "QLabel { background-color: #ff9800; }")  # Orange for active
        self.completed_label.setStyleSheet(base_style + "QLabel { background-color: #4CAF50; }")  # Green for success
        self.remaining_label.setStyleSheet(base_style + "QLabel { background-color: #2196F3; }")  # Blue for pending
        
        # Add to layout
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.downloading_label)
        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.remaining_label)
        stats_layout.addStretch()
        
        stats_container.setLayout(stats_layout)
        main_layout.addWidget(stats_container)
        
        # Scroll area for queue items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #444; border-radius: 4px; background-color: #252526; }")
        
        self.queue_widget = QWidget()
        self.queue_layout = QVBoxLayout()
        self.queue_layout.setSpacing(5)
        self.queue_layout.setContentsMargins(10, 10, 10, 10)
        self.queue_layout.addStretch()
        
        self.queue_widget.setLayout(self.queue_layout)
        scroll.setWidget(self.queue_widget)
        
        main_layout.addWidget(scroll, 1)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.start_button = QPushButton("Start Downloads")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.start_button.clicked.connect(self.start_downloads)
        control_layout.addWidget(self.start_button)
        
        self.pause_all_button = QPushButton("Pause All")
        self.pause_all_button.setEnabled(False)
        self.pause_all_button.clicked.connect(self.pause_all)
        control_layout.addWidget(self.pause_all_button)
        
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_completed_button.clicked.connect(self.clear_completed)
        control_layout.addWidget(self.clear_completed_button)
        
        main_layout.addLayout(control_layout)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage("Ready")
        self.setStatusBar(self.statusBar)
        
        # Initialize stats
        self.update_stats()
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        settings_action = file_menu.addAction('Settings')
        settings_action.triggered.connect(self.show_settings)
        
        history_action = file_menu.addAction('History')
        history_action.triggered.connect(self.show_history)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
    
    def add_urls(self):
        """Add URLs to the download queue."""
        urls_text = self.url_text_edit.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, "No URLs", "Please enter at least one YouTube URL.")
            return
        
        # Parse URLs
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Validate URLs
        valid_urls = []
        invalid_urls = []
        for url in urls:
            if self.is_valid_youtube_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        # Show invalid URLs warning
        if invalid_urls:
            QMessageBox.warning(self, "Invalid URLs", 
                              f"The following URLs are not valid YouTube URLs:\n\n" + 
                              "\n".join(invalid_urls))
        
        if not valid_urls:
            self.url_text_edit.clear()
            return
        
        # Filter out URLs already in queue
        urls_to_add = [url for url in valid_urls if not self.download_queue.get_item(url)]
        
        if not urls_to_add:
            QMessageBox.information(self, "No New URLs", "All URLs are already in the queue.")
            self.url_text_edit.clear()
            return
        
        # Disable the button to prevent multiple clicks
        self.add_urls_button.setEnabled(False)
        self.url_text_edit.setEnabled(False)
        
        # Show progress dialog
        self.progress_dialog = QProgressDialog("Fetching video information...", "Cancel", 0, len(urls_to_add), self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #252526;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        self.progress_dialog.show()
        
        # Create worker thread for fetching video info
        self.info_thread = QThread()
        self.info_worker = VideoInfoWorker(urls_to_add)
        self.info_worker.moveToThread(self.info_thread)
        
        # Connect signals
        self.info_thread.started.connect(self.info_worker.fetch_all_info)
        self.info_worker.progress_updated.connect(lambda current, total: self.progress_dialog.setValue(current))
        self.info_worker.all_info_fetched.connect(lambda results: self.on_video_info_fetched(results, len(urls_to_add)))
        self.info_worker.finished.connect(self.info_thread.quit)
        self.info_worker.finished.connect(self.info_worker.deleteLater)
        self.info_thread.finished.connect(self.info_thread.deleteLater)
        self.progress_dialog.canceled.connect(self.info_thread.requestInterruption)
        
        # Start the thread
        self.info_thread.start()
        
        # Clear URL input immediately for better UX
        self.url_text_edit.clear()
    
    def on_video_info_fetched(self, results, total_count):
        """Handle video information fetched from worker thread."""
        try:
            if self.progress_dialog.wasCanceled():
                self.progress_dialog.close()
                # Re-enable controls if canceled
                self.add_urls_button.setEnabled(True)
                self.url_text_edit.setEnabled(True)
                return
            
            # Add items to queue
            added_count = 0
            for url, title in results:
                # Create download item
                item = DownloadItem(url=url, title=title, status="queued")
                self.download_queue.add(item)
                added_count += 1
            
            # Close progress dialog
            self.progress_dialog.close()
            
            # Update queue display
            self.update_queue_display()
            self.update_stats()
            
            # Save queue
            self.download_queue.save()
            
            # Re-enable controls
            self.add_urls_button.setEnabled(True)
            self.url_text_edit.setEnabled(True)
            
            self.statusBar.showMessage(f"Added {added_count} video(s) to queue")
        except Exception as e:
            # Re-enable controls even if there's an error
            self.add_urls_button.setEnabled(True)
            self.url_text_edit.setEnabled(True)
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
            QMessageBox.critical(self, "Error", f"An error occurred while adding URLs:\n{str(e)}")
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL."""
        valid_patterns = ['youtube.com/watch', 'youtu.be/', 'youtube.com/embed/']
        return any(pattern in url for pattern in valid_patterns)
    
    def browse_folder(self):
        """Browse for download folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.settings.download_folder = folder
            self.folder_path_label.setText(folder)
            self.statusBar.showMessage(f"Download folder: {folder}")
    
    def start_downloads(self):
        """Start downloading videos in the queue."""
        if not self.settings.download_folder:
            QMessageBox.warning(self, "No Folder", "Please select a download folder first.")
            return
        
        queued_items = self.download_queue.get_queued_items()
        if not queued_items:
            QMessageBox.information(self, "Empty Queue", "No videos in queue to download.")
            return
        
        # Start downloads
        self.download_manager.download_multiple(queued_items, self.settings)
        self.pause_all_button.setEnabled(True)
        self.statusBar.showMessage(f"Started downloading {len(queued_items)} video(s)")
    
    def pause_all(self):
        """Pause all active downloads."""
        # Update status for all downloading items
        for item in self.download_queue.items:
            if item.status == "downloading":
                item.status = "paused"
        
        self.download_manager.stop_all()
        self.pause_all_button.setEnabled(False)
        
        # Update all widgets
        self.update_queue_display()
        self.update_stats()
        self.statusBar.showMessage("Downloads paused")
    
    def update_stats(self):
        """Update the statistics display."""
        total = len(self.download_queue.items)
        downloading = len([item for item in self.download_queue.items if item.status == "downloading"])
        completed = len([item for item in self.download_queue.items if item.status == "completed"])
        remaining = total - completed
        
        self.total_label.setText(f"Total: {total}")
        self.downloading_label.setText(f"Downloading: {downloading}")
        self.completed_label.setText(f"Completed: {completed}")
        self.remaining_label.setText(f"Remaining: {remaining}")
    
    def clear_completed(self):
        """Remove completed items from queue."""
        completed_count = len([item for item in self.download_queue.items if item.status == "completed"])
        self.download_queue.clear_completed()
        self.download_queue.save()
        self.update_queue_display()
        self.update_stats()
        self.statusBar.showMessage(f"Cleared {completed_count} completed item(s)")
    
    def remove_download(self, url: str):
        """Remove a download from the queue."""
        item = self.download_queue.get_item(url)
        if item and item.status in ["downloading", "paused"]:
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                "This download is in progress. Do you want to cancel it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.download_queue.remove(url)
        self.download_queue.save()
        self.update_queue_display()
        self.update_stats()
        self.statusBar.showMessage("Item removed from queue")
    
    def update_queue_display(self):
        """Update the queue display."""
        # Remove all widgets
        while self.queue_layout.count() > 1:  # Keep stretch
            item = self.queue_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Re-add widgets
        for item in self.download_queue.items:
            widget = DownloadItemWidget(item)
            widget.remove_button.clicked.connect(lambda checked, u=item.url: self.remove_download(u))
            widget.retry_button.clicked.connect(lambda checked, u=item.url: self.retry_download(u))
            self.queue_layout.insertWidget(self.queue_layout.count() - 1, widget)
    
    def on_download_started(self, url: str):
        """Handle download started."""
        item = self.download_queue.get_item(url)
        if item:
            item.status = "downloading"
            self.update_queue_display()
            self.update_stats()
    
    def on_progress_updated(self, url: str, progress_info: dict):
        """Handle progress update."""
        # Update the download item data
        item = self.download_queue.get_item(url)
        if item:
            # Update the download item with progress info
            item.progress = progress_info.get('progress', 0.0)
            
            # Update speed
            speed_bytes = progress_info.get('speed', 0)
            if speed_bytes > 0:
                speed_mb = speed_bytes / (1024 * 1024)
                item.speed = f"{speed_mb:.2f} MB/s"
            
            # Update ETA
            eta_seconds = progress_info.get('eta', 0)
            if eta_seconds and eta_seconds > 0:
                minutes = int(eta_seconds // 60)
                seconds = int(eta_seconds % 60)
                item.eta = f"{minutes:02d}:{seconds:02d}"
            
            # Update file size
            total_bytes = progress_info.get('total_bytes', 0)
            if total_bytes > 0:
                size_mb = total_bytes / (1024 * 1024)
                item.file_size = f"{size_mb:.2f} MB"
            
            # Find the widget for this URL and update it
            for i in range(self.queue_layout.count() - 1):
                layout_item = self.queue_layout.itemAt(i)
                if layout_item is None:
                    continue
                widget = layout_item.widget()
                if isinstance(widget, DownloadItemWidget) and widget.download_item.url == url:
                    widget.update_progress(progress_info)
                    break
    
    def on_download_completed(self, url: str, filepath: str):
        """Handle download completed."""
        item = self.download_queue.get_item(url)
        if item:
            item.status = "completed"
            item.output_path = filepath
            item.progress = 100.0
            
            # Add to history
            self.history.add_download(
                url=url,
                title=item.title,
                file_path=filepath,
                file_size=item.file_size,
                video_quality=self.settings.video_quality,
                status="completed"
            )
            
            self.update_queue_display()
            self.update_stats()
            self.statusBar.showMessage(f"Download completed: {item.title}")
            
            # Check if all downloads are complete
            active_downloads = [i for i in self.download_queue.items if i.status in ["downloading", "queued"]]
            if not active_downloads:
                self.pause_all_button.setEnabled(False)
    
    def on_download_failed(self, url: str, error_message: str):
        """Handle download failed."""
        item = self.download_queue.get_item(url)
        if item:
            item.status = "error"
            item.file_size = error_message
            self.update_queue_display()
            self.update_stats()
            self.statusBar.showMessage(f"Download failed: {error_message}")
    
    def retry_download(self, url: str):
        """Retry a failed download."""
        item = self.download_queue.get_item(url)
        if item and item.status == "error":
            # Reset the item status and progress
            item.status = "queued"
            item.progress = 0.0
            item.speed = "0.0 MB/s"
            item.eta = ""
            item.file_size = ""
            item.output_path = ""
            
            # Start the download
            self.download_manager.download_multiple([item], self.settings)
            
            # Save queue
            self.download_queue.save()
            
            # Update display
            self.update_queue_display()
            self.update_stats()
            self.statusBar.showMessage("Retrying download...")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.get_settings()
            self.settings.save()
            self.download_manager.max_workers = self.settings.max_concurrent_downloads
            self.statusBar.showMessage("Settings saved")
    
    def show_history(self):
        """Show history dialog."""
        dialog = HistoryDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog."""
        from version import get_version
        QMessageBox.about(
            self,
            "About Videoteka",
            f"Videoteka v{get_version()}\n\n"
            "A desktop application for downloading YouTube videos\n"
            "with support for parallel downloads and quality settings.\n\n"
            "Author: Vinícius Gregório\n"
            "GitHub: https://github.com/vncgregorio/videoteka\n\n"
            "Built with PyQt6 and yt-dlp\n\n"
            "Licensed under GPLv3"
        )
    
    def closeEvent(self, event: QCloseEvent):
        """Handle application close event."""
        # Save queue before closing
        self.download_queue.save()
        
        # Stop any running downloads
        self.download_manager.stop_all()
        
        # Accept the close event
        event.accept()

