import sys
import json
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTextEdit, QPushButton,
                             QMessageBox, QFrame, QGraphicsDropShadowEffect,
                             QProgressBar, QTabWidget, QListWidget, QListWidgetItem,
                             QSplitter, QGroupBox, QGridLayout, QSpinBox,
                             QCheckBox, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QDateTime, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QLinearGradient, QPainter, QBrush, QPixmap


class HashWorker(QThread):
    """Worker thread to handle API requests without blocking the UI"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, text, api_url):
        super().__init__()
        self.text = text
        self.api_url = api_url

    def run(self):
        try:
            self.progress_update.emit(20)
            headers = {'Content-Type': 'application/json'}
            data = {'text': self.text}

            self.progress_update.emit(50)
            response = requests.post(self.api_url, json=data, headers=headers, timeout=10)

            self.progress_update.emit(80)

            if response.status_code == 200:
                self.progress_update.emit(100)
                self.result_ready.emit(response.json())
            else:
                error_data = response.json()
                error_msg = error_data.get('error', f'Server returned status code: {response.status_code}')
                self.error_occurred.emit(error_msg)
        except requests.exceptions.Timeout:
            self.error_occurred.emit("⏱️ Request timed out. Please check your connection.")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit(
                "🔌 Could not connect to the server. Make sure the Flask app is running on http://127.0.0.1:5000")
        except json.JSONDecodeError:
            self.error_occurred.emit("❌ Invalid response from server.")
        except Exception as e:
            self.error_occurred.emit(f"⚠️ An unexpected error occurred: {str(e)}")


class AnimatedButton(QPushButton):
    """Custom animated button with hover effects"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


class ModernCard(QFrame):
    """Modern card widget with shadow and hover effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        self.setup_shadow()

    def setup_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)


class APIHasherDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_url = "http://127.0.0.1:5000/api/hash"
        self.history = []
        self.dark_mode = False
        self.init_ui()
        self.apply_light_theme()

    def init_ui(self):
        self.setWindowTitle("🔐 API-Hasher Pro - Windows Edition")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top toolbar
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(60)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 0, 20, 0)

        # Logo and title
        logo_label = QLabel("🔐")
        logo_label.setStyleSheet("font-size: 32px;")
        toolbar_layout.addWidget(logo_label)

        app_title = QLabel("API-Hasher Pro")
        app_title.setObjectName("appTitle")
        toolbar_layout.addWidget(app_title)

        toolbar_layout.addStretch()

        # Settings buttons
        self.api_input = QLineEdit(self.api_url)
        self.api_input.setObjectName("apiInput")
        self.api_input.setPlaceholderText("API Endpoint")
        self.api_input.textChanged.connect(self.update_api_url)
        toolbar_layout.addWidget(self.api_input)

        self.theme_button = AnimatedButton("🌙 Dark Mode")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar_layout.addWidget(self.theme_button)

        main_layout.addWidget(toolbar)

        # Main content area with modern layout
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Left side - Main functionality
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(20)

        # Input card
        input_card = ModernCard()
        input_card_layout = QVBoxLayout(input_card)

        input_header = QLabel("📝 Text Input")
        input_header.setObjectName("cardHeader")
        input_card_layout.addWidget(input_header)

        # Text input with line numbers simulation
        input_container = QWidget()
        input_container_layout = QHBoxLayout(input_container)
        input_container_layout.setContentsMargins(0, 0, 0, 0)

        self.text_input = QTextEdit()
        self.text_input.setObjectName("textInput")
        self.text_input.setPlaceholderText(
            "Enter your text here...\n\nYou can paste:\n• Passwords\n• API Keys\n• Source Code\n• Any text content")
        self.text_input.textChanged.connect(self.on_text_changed)
        input_container_layout.addWidget(self.text_input)

        input_card_layout.addWidget(input_container)

        # Input stats
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 10, 0, 0)

        self.char_count = QLabel("📊 Characters: 0")
        self.char_count.setObjectName("statsLabel")
        stats_layout.addWidget(self.char_count)

        self.word_count = QLabel("📝 Words: 0")
        self.word_count.setObjectName("statsLabel")
        stats_layout.addWidget(self.word_count)

        self.line_count = QLabel("📋 Lines: 0")
        self.line_count.setObjectName("statsLabel")
        stats_layout.addWidget(self.line_count)

        stats_layout.addStretch()

        input_card_layout.addWidget(stats_widget)

        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)

        self.hash_button = AnimatedButton("⚡ Generate SHA-256 Hash")
        self.hash_button.setObjectName("primaryButton")
        self.hash_button.clicked.connect(self.calculate_hash)
        button_layout.addWidget(self.hash_button)

        self.clear_button = AnimatedButton("🗑️ Clear All")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

        self.paste_button = AnimatedButton("📋 Paste")
        self.paste_button.setObjectName("secondaryButton")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        button_layout.addWidget(self.paste_button)

        input_card_layout.addWidget(button_container)

        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        input_card_layout.addWidget(self.progress_bar)

        left_layout.addWidget(input_card)

        # Result card
        self.result_card = ModernCard()
        self.result_card.hide()
        result_card_layout = QVBoxLayout(self.result_card)

        result_header = QLabel("✅ Hash Result")
        result_header.setObjectName("cardHeader")
        result_card_layout.addWidget(result_header)

        # Hash display with copy functionality
        hash_container = QWidget()
        hash_container.setObjectName("hashContainer")
        hash_layout = QVBoxLayout(hash_container)

        self.hash_display = QTextEdit()
        self.hash_display.setObjectName("hashDisplay")
        self.hash_display.setReadOnly(True)
        self.hash_display.setMaximumHeight(80)
        hash_layout.addWidget(self.hash_display)

        # Result actions
        result_actions = QWidget()
        result_actions_layout = QHBoxLayout(result_actions)
        result_actions_layout.setSpacing(10)

        self.copy_hash_btn = AnimatedButton("📋 Copy Hash")
        self.copy_hash_btn.setObjectName("actionButton")
        self.copy_hash_btn.clicked.connect(self.copy_hash)
        result_actions_layout.addWidget(self.copy_hash_btn)

        self.save_history_btn = AnimatedButton("💾 Save to History")
        self.save_history_btn.setObjectName("actionButton")
        self.save_history_btn.clicked.connect(self.save_to_history)
        result_actions_layout.addWidget(self.save_history_btn)

        self.compare_btn = AnimatedButton("🔍 Compare")
        self.compare_btn.setObjectName("actionButton")
        self.compare_btn.clicked.connect(self.open_compare_dialog)
        result_actions_layout.addWidget(self.compare_btn)

        hash_layout.addWidget(result_actions)

        result_card_layout.addWidget(hash_container)

        # Hash info
        self.hash_info = QLabel()
        self.hash_info.setObjectName("hashInfo")
        result_card_layout.addWidget(self.hash_info)

        left_layout.addWidget(self.result_card)
        left_layout.addStretch()

        # Right side - History and tools
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(20)

        # History card
        history_card = ModernCard()
        history_card_layout = QVBoxLayout(history_card)

        history_header_widget = QWidget()
        history_header_layout = QHBoxLayout(history_header_widget)
        history_header_layout.setContentsMargins(0, 0, 0, 0)

        history_header = QLabel("📜 History")
        history_header.setObjectName("cardHeader")
        history_header_layout.addWidget(history_header)

        history_header_layout.addStretch()

        self.clear_history_btn = AnimatedButton("Clear")
        self.clear_history_btn.setObjectName("smallButton")
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_header_layout.addWidget(self.clear_history_btn)

        history_card_layout.addWidget(history_header_widget)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("🔍 Search history...")
        self.search_input.textChanged.connect(self.filter_history)
        history_card_layout.addWidget(self.search_input)

        # History list
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        history_card_layout.addWidget(self.history_list)

        right_layout.addWidget(history_card)

        # Quick tools card
        tools_card = ModernCard()
        tools_card_layout = QVBoxLayout(tools_card)

        tools_header = QLabel("🛠️ Quick Tools")
        tools_header.setObjectName("cardHeader")
        tools_card_layout.addWidget(tools_header)

        # REMOVED: Batch processing
        # self.batch_check = QCheckBox("Enable Batch Processing")
        # self.batch_check.setObjectName("toolOption")
        # tools_card_layout.addWidget(self.batch_check)

        # Auto-copy
        self.auto_copy_check = QCheckBox("Auto-copy hash to clipboard")
        self.auto_copy_check.setObjectName("toolOption")
        tools_card_layout.addWidget(self.auto_copy_check)

        # Hash format
        format_widget = QWidget()
        format_layout = QHBoxLayout(format_widget)
        format_layout.setContentsMargins(0, 0, 0, 0)

        format_label = QLabel("Format:")
        format_label.setObjectName("toolLabel")
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["Lowercase", "Uppercase", "With Spaces"])
        self.format_combo.currentTextChanged.connect(self.update_hash_format)
        format_layout.addWidget(self.format_combo)

        format_layout.addStretch()

        tools_card_layout.addWidget(format_widget)

        right_layout.addWidget(tools_card)
        right_layout.addStretch()

        # Add splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        content_layout.addWidget(splitter)
        main_layout.addWidget(content_widget)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("statusBar")
        self.update_status("Ready")

        # Initialize current result
        self.current_result = None

    def apply_light_theme(self):
        """Apply light theme styles"""
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #f5f5f5;
                    }

                    #toolbar {
                        background-color: #ffffff;
                        border-bottom: 1px solid #e0e0e0;
                    }

                    #appTitle {
                        font-size: 24px;
                        font-weight: 700;
                        color: #1976d2;
                        margin-left: 10px;
                    }

                    #apiInput {
                        padding: 8px 12px;
                        border: 2px solid #e0e0e0;
                        border-radius: 6px;
                        font-size: 13px;
                        min-width: 250px;
                        background-color: #fafafa;
                    }

                    #apiInput:focus {
                        border-color: #1976d2;
                        background-color: #ffffff;
                    }

                    #themeButton {
                        background-color: #424242;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                    }

                    #themeButton:hover {
                        background-color: #616161;
                    }

                    #contentArea {
                        background-color: #f5f5f5;
                    }

                    #modernCard {
                        background-color: #ffffff;
                        border-radius: 12px;
                        padding: 20px;
                        border: 1px solid #e0e0e0;
                    }

                    #cardHeader {
                        font-size: 18px;
                        font-weight: 700;
                        color: #212121;
                        margin-bottom: 15px;
                    }

                    #textInput {
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        background-color: #fafafa;
                        min-height: 250px;
                    }

                    #textInput:focus {
                        border-color: #1976d2;
                        background-color: #ffffff;
                    }

                    #statsLabel {
                        color: #757575;
                        font-size: 13px;
                        margin-right: 20px;
                    }

                    #primaryButton {
                        background-color: #1976d2;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        font-size: 15px;
                        font-weight: 600;
                    }

                    #primaryButton:hover {
                        background-color: #1565c0;
                    }

                    #primaryButton:pressed {
                        background-color: #0d47a1;
                    }

                    #primaryButton:disabled {
                        background-color: #bbdefb;
                        color: #90caf9;
                    }

                    #secondaryButton {
                        background-color: #757575;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 20px;
                        font-size: 15px;
                        font-weight: 600;
                    }

                    #secondaryButton:hover {
                        background-color: #616161;
                    }

                    #progressBar {
                        border: none;
                        border-radius: 4px;
                        background-color: #e3f2fd;
                        height: 6px;
                        margin-top: 10px;
                    }

                    #progressBar::chunk {
                        background-color: #1976d2;
                        border-radius: 4px;
                    }

                    #hashContainer {
                        background-color: #e3f2fd;
                        border-radius: 8px;
                        padding: 15px;
                        border: 1px solid #90caf9;
                    }

                    #hashDisplay {
                        background-color: transparent;
                        border: none;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 16px;
                        font-weight: 600;
                        color: #0d47a1;
                    }

                    #actionButton {
                        background-color: #43a047;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-size: 13px;
                        font-weight: 600;
                    }

                    #actionButton:hover {
                        background-color: #388e3c;
                    }

                    #hashInfo {
                        color: #616161;
                        font-size: 12px;
                        margin-top: 10px;
                    }

                    #searchInput {
                        padding: 8px 12px;
                        border: 2px solid #e0e0e0;
                        border-radius: 6px;
                        font-size: 13px;
                        background-color: #fafafa;
                        margin-bottom: 10px;
                    }

                    #searchInput:focus {
                        border-color: #1976d2;
                        background-color: #ffffff;
                    }

                    #historyList {
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        background-color: #fafafa;
                        padding: 5px;
                    }

                    #historyList::item {
                        padding: 12px;
                        margin: 3px;
                        border-radius: 6px;
                        background-color: #ffffff;
                        border: 1px solid #e0e0e0;
                    }

                    #historyList::item:hover {
                        background-color: #e3f2fd;
                        border-color: #90caf9;
                    }

                    #historyList::item:selected {
                        background-color: #1976d2;
                        color: white;
                        border-color: #1976d2;
                    }

                    #smallButton {
                        background-color: #ef5350;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                        font-weight: 600;
                    }

                    #smallButton:hover {
                        background-color: #e53935;
                    }

                    #toolOption {
                        color: #424242;
                        font-size: 13px;
                        margin: 8px 0;
                    }

                    #toolOption::indicator {
                        width: 18px;
                        height: 18px;
                    }

                    #toolLabel {
                        color: #616161;
                        font-size: 13px;
                        margin-right: 10px;
                    }

                    QComboBox {
                        padding: 6px 12px;
                        border: 2px solid #e0e0e0;
                        border-radius: 6px;
                        background-color: #fafafa;
                        min-width: 120px;
                    }

                    QComboBox:hover {
                        border-color: #bdbdbd;
                    }

                    QComboBox::drop-down {
                        border: none;
                    }

                    #statusBar {
                        background-color: #424242;
                        color: white;
                        font-size: 12px;
                    }

                    QMessageBox {
                        background-color: #ffffff;
                    }

                    QMessageBox QPushButton {
                        background-color: #1976d2;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        min-width: 80px;
                    }
                """)

    def apply_dark_theme(self):
        """Apply dark theme styles"""
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #121212;
                    }

                    #toolbar {
                        background-color: #1e1e1e;
                        border-bottom: 1px solid #333333;
                    }

                    #appTitle {
                        font-size: 24px;
                        font-weight: 700;
                        color: #64b5f6;
                        margin-left: 10px;
                    }

                    #apiInput {
                        padding: 8px 12px;
                        border: 2px solid #333333;
                        border-radius: 6px;
                        font-size: 13px;
                        min-width: 250px;
                        background-color: #2a2a2a;
                        color: #ffffff;
                    }

                    #apiInput:focus {
                        border-color: #64b5f6;
                        background-color: #333333;
                    }

                    #themeButton {
                        background-color: #ffc107;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                    }

                    #themeButton:hover {
                        background-color: #ffb300;
                    }

                    #contentArea {
                        background-color: #121212;
                    }

                    #modernCard {
                        background-color: #1e1e1e;
                        border-radius: 12px;
                        padding: 20px;
                        border: 1px solid #333333;
                    }

                    #cardHeader {
                        font-size: 18px;
                        font-weight: 700;
                        color: #ffffff;
                        margin-bottom: 15px;
                    }

                    #textInput {
                        border: 2px solid #333333;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        background-color: #2a2a2a;
                        color: #ffffff;
                        min-height: 250px;
                    }

                    #textInput:focus {
                        border-color: #64b5f6;
                        background-color: #333333;
                    }

                    #statsLabel {
                        color: #b0b0b0;
                        font-size: 13px;
                        margin-right: 20px;
                    }

                    #primaryButton {
                        background-color: #64b5f6;
                        color: #000000;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        font-size: 15px;
                        font-weight: 600;
                    }

                    #primaryButton:hover {
                        background-color: #42a5f5;
                    }

                    #primaryButton:disabled {
                        background-color: #37474f;
                        color: #546e7a;
                    }

                    #secondaryButton {
                        background-color: #546e7a;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 20px;
                        font-size: 15px;
                        font-weight: 600;
                    }

                    #secondaryButton:hover {
                        background-color: #455a64;
                    }

                    #progressBar {
                        border: none;
                        border-radius: 4px;
                        background-color: #37474f;
                        height: 6px;
                        margin-top: 10px;
                    }

                    #progressBar::chunk {
                        background-color: #64b5f6;
                        border-radius: 4px;
                    }

                    #hashContainer {
                        background-color: #263238;
                        border-radius: 8px;
                        padding: 15px;
                        border: 1px solid #37474f;
                    }

                    #hashDisplay {
                        background-color: transparent;
                        border: none;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 16px;
                        font-weight: 600;
                        color: #81c784;
                    }

                    #actionButton {
                        background-color: #66bb6a;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-size: 13px;
                        font-weight: 600;
                    }

                    #actionButton:hover {
                        background-color: #4caf50;
                    }

                    #hashInfo {
                        color: #b0b0b0;
                        font-size: 12px;
                        margin-top: 10px;
                    }

                    #searchInput {
                        padding: 8px 12px;
                        border: 2px solid #333333;
                        border-radius: 6px;
                        font-size: 13px;
                        background-color: #2a2a2a;
                        color: #ffffff;
                        margin-bottom: 10px;
                    }

                    #historyList {
                        border: 1px solid #333333;
                        border-radius: 8px;
                        background-color: #2a2a2a;
                        padding: 5px;
                    }

                    #historyList::item {
                        padding: 12px;
                        margin: 3px;
                        border-radius: 6px;
                        background-color: #333333;
                        border: 1px solid #424242;
                        color: #ffffff;
                    }

                    #historyList::item:hover {
                        background-color: #37474f;
                        border-color: #546e7a;
                    }

                    #historyList::item:selected {
                        background-color: #64b5f6;
                        color: #000000;
                        border-color: #64b5f6;
                    }

                    #smallButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                        font-weight: 600;
                    }

                    #toolOption {
                        color: #e0e0e0;
                        font-size: 13px;
                        margin: 8px 0;
                    }

                    #toolLabel {
                        color: #b0b0b0;
                        font-size: 13px;
                        margin-right: 10px;
                    }

                    QComboBox {
                        padding: 6px 12px;
                        border: 2px solid #333333;
                        border-radius: 6px;
                        background-color: #2a2a2a;
                        color: #ffffff;
                        min-width: 120px;
                    }

                    QComboBox::drop-down {
                        border: none;
                    }

                    #statusBar {
                        background-color: #1e1e1e;
                        color: #b0b0b0;
                        font-size: 12px;
                    }
                """)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
            self.theme_button.setText("☀️ Light Mode")
        else:
            self.apply_light_theme()
            self.theme_button.setText("🌙 Dark Mode")

    def update_api_url(self, text):
        """Update API URL from input field"""
        self.api_url = text.strip()
        self.update_status(f"API endpoint updated: {self.api_url}")

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(f"🔹 {message}")

    def on_text_changed(self):
        """Update statistics when text changes"""
        text = self.text_input.toPlainText()

        # Character count
        char_count = len(text)
        self.char_count.setText(f"📊 Characters: {char_count:,}")

        # Word count
        words = text.split()
        word_count = len(words)
        self.word_count.setText(f"📝 Words: {word_count:,}")

        # Line count
        lines = text.split('\n')
        line_count = len(lines)
        self.line_count.setText(f"📋 Lines: {line_count:,}")

    def paste_from_clipboard(self):
        """Paste text from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.text_input.setPlainText(text)
            self.update_status("Text pasted from clipboard")

    def clear_all(self):
        """Clear all input and results"""
        self.text_input.clear()
        self.hash_display.clear()
        self.result_card.hide()
        self.update_status("All cleared")

    def calculate_hash(self):
        """Calculate hash for the input text"""
        text = self.text_input.toPlainText()

        if not text:
            self.show_error("Please enter some text to hash!")
            return

        # Disable button and show progress
        self.hash_button.setEnabled(False)
        self.hash_button.setText("⏳ Processing...")
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        # Start worker thread
        self.worker = HashWorker(text, self.api_url)
        self.worker.result_ready.connect(self.on_hash_result)
        self.worker.error_occurred.connect(self.on_hash_error)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished.connect(self.on_request_finished)
        self.worker.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def on_hash_result(self, result):
        """Handle successful hash result"""
        self.current_result = result

        # Display hash
        hash_value = result['hashed_value']

        # Apply format if needed
        format_type = self.format_combo.currentText()
        if format_type == "Uppercase":
            hash_value = hash_value.upper()
        elif format_type == "With Spaces":
            hash_value = ' '.join([hash_value[i:i + 2] for i in range(0, len(hash_value), 2)])

        self.hash_display.setPlainText(hash_value)

        # Update hash info
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.hash_info.setText(f"Generated at: {timestamp} | Length: {len(hash_value)} characters")

        # Show result card
        self.result_card.show()

        # Auto-copy if enabled
        if self.auto_copy_check.isChecked():
            self.copy_hash()
            self.update_status("Hash generated and copied to clipboard!")
        else:
            self.update_status("Hash generated successfully!")

        # REMOVED: Auto-save to history based on batch_check
        # if self.batch_check.isChecked():
        #     self.save_to_history()

    def on_hash_error(self, error_msg):
        """Handle hash generation error"""
        self.show_error(error_msg)
        self.update_status(f"Error: {error_msg}")

    def on_request_finished(self):
        """Clean up after request completion"""
        self.hash_button.setEnabled(True)
        self.hash_button.setText("⚡ Generate SHA-256 Hash")
        self.progress_bar.hide()

    def show_error(self, message):
        """Show error message dialog"""
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def copy_hash(self):
        """Copy hash to clipboard"""
        clipboard = QApplication.clipboard()
        hash_text = self.hash_display.toPlainText()
        clipboard.setText(hash_text)
        self.update_status("Hash copied to clipboard!")

    def save_to_history(self):
        """Save current result to history"""
        if not self.current_result:
            return

        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        original_text = self.current_result['original_text']
        hash_value = self.current_result['hashed_value']

        # Create preview
        preview = original_text[:50] + "..." if len(original_text) > 50 else original_text
        preview = preview.replace('\n', ' ')

        # Create history entry
        history_entry = {
            'timestamp': timestamp,
            'original_text': original_text,
            'hash': hash_value,
            'preview': preview
        }

        self.history.append(history_entry)

        # Add to history list
        item_text = f"🕐 {timestamp}\n📝 {preview}\n🔐 {hash_value[:32]}..."
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, history_entry)
        self.history_list.insertItem(0, item)

        self.update_status("Saved to history!")

    def load_from_history(self, item):
        """Load text from history item"""
        history_entry = item.data(Qt.ItemDataRole.UserRole)
        if history_entry:
            self.text_input.setPlainText(history_entry['original_text'])
            self.hash_display.setPlainText(history_entry['hash'])
            self.result_card.show()
            self.update_status("Loaded from history")

    def filter_history(self, search_text):
        """Filter history items based on search text"""
        search_text = search_text.lower()

        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            history_entry = item.data(Qt.ItemDataRole.UserRole)

            if history_entry:
                # Search in preview and hash
                if (search_text in history_entry['preview'].lower() or
                        search_text in history_entry['hash'].lower() or
                        search_text in history_entry['timestamp'].lower()):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def clear_history(self):
        """Clear all history"""
        reply = QMessageBox.question(
            self,
            'Clear History',
            'Are you sure you want to clear all history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.history_list.clear()
            self.update_status("History cleared")

    def update_hash_format(self, format_type):
        """Update hash display format"""
        if self.current_result and self.hash_display.toPlainText():
            hash_value = self.current_result['hashed_value']

            if format_type == "Uppercase":
                hash_value = hash_value.upper()
            elif format_type == "With Spaces":
                hash_value = ' '.join([hash_value[i:i + 2] for i in range(0, len(hash_value), 2)])

            self.hash_display.setPlainText(hash_value)

    def open_compare_dialog(self):
        """Open hash comparison dialog"""
        if not self.current_result:
            self.show_error("No hash to compare! Generate a hash first.")
            return

        dialog = QMessageBox()
        dialog.setWindowTitle("Compare Hash")
        dialog.setText("Enter a hash to compare with the current hash:")

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter hash to compare...")
        dialog.layout().addWidget(input_field, 1, 1)

        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if dialog.exec() == QMessageBox.StandardButton.Ok:
            compare_hash = input_field.text().strip().lower()
            current_hash = self.current_result['hashed_value'].lower()

            if compare_hash == current_hash:
                QMessageBox.information(self, "Match!", "✅ The hashes match!")
            else:
                QMessageBox.warning(self, "No Match", "❌ The hashes do not match!")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application font
    font = QFont()
    font.setFamily("Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif")
    font.setPointSize(10)
    app.setFont(font)

    # Create and show main window
    window = APIHasherDesktop()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()