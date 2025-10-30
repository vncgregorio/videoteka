"""Custom widget for displaying download items in the queue."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton
)
from PyQt6.QtCore import Qt
from models.settings import DownloadItem


class DownloadItemWidget(QWidget):
    """Widget displaying a single download item with progress."""
    
    def __init__(self, download_item: DownloadItem, parent=None):
        super().__init__(parent)
        self.download_item = download_item
        self.init_ui()
        self.update_display()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Top row: Title and actions
        top_layout = QHBoxLayout()
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.title_label, 1)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(self.status_label)
        
        # Control buttons
        self.pause_button = QPushButton("Pause")
        self.pause_button.setMaximumWidth(80)
        self.pause_button.clicked.connect(self.toggle_pause)
        top_layout.addWidget(self.pause_button)
        
        self.retry_button = QPushButton("Retry")
        self.retry_button.setMaximumWidth(80)
        self.retry_button.setVisible(False)
        top_layout.addWidget(self.retry_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setMaximumWidth(80)
        top_layout.addWidget(self.remove_button)
        
        layout.addLayout(top_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Bottom row: Info
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_layout.addWidget(self.info_label, 1)
        
        self.eta_label = QLabel()
        self.eta_label.setStyleSheet("color: #666; font-size: 11px;")
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_layout.addWidget(self.eta_label)
        
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        
        # Set item-specific style (dark theme)
        self.setStyleSheet("""
            DownloadItemWidget {
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                background-color: #2d2d2d;
                margin: 2px;
            }
            DownloadItemWidget:hover {
                background-color: #353535;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                height: 20px;
                background-color: #252526;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Style the retry button
        self.retry_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fb8c00;
            }
            QPushButton:pressed {
                background-color: #f57c00;
            }
        """)
    
    def update_display(self):
        """Update the display with current download item data."""
        # Title and status
        self.title_label.setText(self.download_item.title or "Unknown Video")
        
        status = self.download_item.status
        self.status_label.setText(status.capitalize())
        
        # Color the status label based on state
        if status == "error":
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")  # Red for error
        elif status == "completed":
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")  # Green for completed
        elif status == "downloading":
            self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")  # Orange for downloading
        elif status == "paused":
            self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")  # Yellow for paused
        else:
            self.status_label.setStyleSheet("color: #ffffff;")  # Default white for queued
        
        # Progress bar
        progress = int(self.download_item.progress)
        self.progress_bar.setValue(progress)
        
        # Info display
        if status == "downloading":
            size = self.download_item.file_size if self.download_item.file_size else "Unknown size"
            info = f"{self.download_item.speed} | {size}"
            self.info_label.setText(info)
            self.eta_label.setText(f"ETA: {self.download_item.eta}")
        elif status == "queued":
            self.info_label.setText("Waiting to start...")
            self.eta_label.setText("")
        elif status == "completed":
            path = self.download_item.output_path if self.download_item.output_path else "Unknown path"
            self.info_label.setText(f"Saved to: {path}")
            self.eta_label.setText("")
        elif status == "error":
            error_msg = self.download_item.file_size if self.download_item.file_size else "Unknown error"
            self.info_label.setText(f"Error: {error_msg}")
            self.eta_label.setText("")
        elif status == "paused":
            self.info_label.setText("Download paused")
            self.eta_label.setText("")
        
        # Button states
        if status in ["downloading", "paused"]:
            self.pause_button.setVisible(True)
            self.pause_button.setText("Pause" if status == "downloading" else "Resume")
            self.retry_button.setVisible(False)
        elif status == "error":
            self.pause_button.setVisible(False)
            self.retry_button.setVisible(True)
        else:
            self.pause_button.setVisible(False)
            self.retry_button.setVisible(False)
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.download_item.status == "downloading":
            self.download_item.status = "paused"
        elif self.download_item.status == "paused":
            self.download_item.status = "queued"
        self.update_display()
    
    def update_progress(self, progress_info: dict):
        """Update progress from download manager."""
        self.download_item.progress = progress_info.get('progress', 0.0)
        
        # Update speed
        speed_bytes = progress_info.get('speed', 0)
        if speed_bytes > 0:
            speed_mb = speed_bytes / (1024 * 1024)
            self.download_item.speed = f"{speed_mb:.2f} MB/s"
        else:
            self.download_item.speed = "0.0 MB/s"
        
        # Update ETA
        eta_seconds = progress_info.get('eta', 0)
        if eta_seconds and eta_seconds > 0:
            minutes = int(eta_seconds // 60)
            seconds = int(eta_seconds % 60)
            self.download_item.eta = f"{minutes:02d}:{seconds:02d}"
        
        # Update file size
        total_bytes = progress_info.get('total_bytes', 0)
        if total_bytes > 0:
            size_mb = total_bytes / (1024 * 1024)
            self.download_item.file_size = f"{size_mb:.2f} MB"
        
        self.update_display()

