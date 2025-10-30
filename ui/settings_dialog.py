"""Settings dialog for configuring download preferences."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QCheckBox, QPushButton, 
    QGroupBox, QFormLayout
)
from models.settings import Settings


class SettingsDialog(QDialog):
    """Dialog for configuring download settings."""
    
    def __init__(self, current_settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = current_settings
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        # Apply styling (dark theme)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
            }
            QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QComboBox:hover, QSpinBox:hover {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #3c3c3c;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
            }
            QCheckBox {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Video Quality Group
        quality_group = QGroupBox("Video Quality")
        quality_layout = QFormLayout()
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p", "audio"])
        self.quality_combo.setCurrentText(self.settings.video_quality)
        quality_layout.addRow(QLabel("Quality:"), self.quality_combo)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "webm", "mkv"])
        self.format_combo.setCurrentText(self.settings.preferred_format)
        quality_layout.addRow(QLabel("Format:"), self.format_combo)
        
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        # Audio Quality Group
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout()
        
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["best", "192k", "128k"])
        self.audio_combo.setCurrentText(self.settings.audio_quality)
        audio_layout.addRow(QLabel("Audio Quality:"), self.audio_combo)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Subtitles Group
        subtitle_group = QGroupBox("Subtitles")
        subtitle_layout = QFormLayout()
        
        self.subtitle_check = QCheckBox()
        self.subtitle_check.setChecked(self.settings.download_subtitles)
        subtitle_layout.addRow(QLabel("Download Subtitles:"), self.subtitle_check)
        
        self.subtitle_lang = QComboBox()
        self.subtitle_lang.addItems(["en", "pt", "es", "fr", "de", "it", "ru", "ja", "ko", "zh"])
        self.subtitle_lang.setCurrentText(self.settings.subtitles_language)
        subtitle_layout.addRow(QLabel("Language:"), self.subtitle_lang)
        
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout()
        
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setMinimum(1)
        self.max_concurrent_spin.setMaximum(10)
        self.max_concurrent_spin.setValue(self.settings.max_concurrent_downloads)
        download_layout.addRow(QLabel("Max Concurrent Downloads:"), self.max_concurrent_spin)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_settings(self) -> Settings:
        """Get the updated settings."""
        self.settings.video_quality = self.quality_combo.currentText()
        self.settings.preferred_format = self.format_combo.currentText()
        self.settings.audio_quality = self.audio_combo.currentText()
        self.settings.download_subtitles = self.subtitle_check.isChecked()
        self.settings.subtitles_language = self.subtitle_lang.currentText()
        self.settings.max_concurrent_downloads = self.max_concurrent_spin.value()
        return self.settings

