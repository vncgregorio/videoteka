"""History dialog for viewing download history."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PyQt6.QtCore import Qt
from utils.database import DownloadHistory


class HistoryDialog(QDialog):
    """Dialog for viewing and managing download history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = DownloadHistory()
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Download History")
        self.setMinimumSize(900, 600)
        
        # Apply styling (dark theme)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTableWidget {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #2d2d2d;
                gridline-color: #444;
                color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
                color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #0078d4;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Download History")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Date", "Size", "Quality", "Status"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self.clear_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_history(self):
        """Load and display download history."""
        downloads = self.history.get_all_downloads()
        
        self.table.setRowCount(len(downloads))
        
        for row, download in enumerate(downloads):
            # Title
            self.table.setItem(row, 0, QTableWidgetItem(download.get('title', 'Unknown')))
            
            # URL
            url_item = QTableWidgetItem(download.get('url', ''))
            url_item.setToolTip(download.get('url', ''))
            self.table.setItem(row, 1, url_item)
            
            # Date
            date = download.get('download_date', '')
            if date:
                # Parse ISO format and format nicely
                date_str = date.split('T')[0]  # Just get date part
            else:
                date_str = 'Unknown'
            self.table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # Size
            self.table.setItem(row, 3, QTableWidgetItem(download.get('file_size', 'Unknown')))
            
            # Quality
            self.table.setItem(row, 4, QTableWidgetItem(download.get('video_quality', 'Unknown')))
            
            # Status
            status = download.get('status', 'completed')
            status_item = QTableWidgetItem(status.capitalize())
            if status == 'completed':
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)
    
    def clear_history(self):
        """Clear all download history."""
        reply = QMessageBox.question(
            self, 
            'Clear History', 
            'Are you sure you want to clear all download history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear_history()
            self.load_history()

