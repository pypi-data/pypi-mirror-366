from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QLineEdit, QComboBox,
                           QFormLayout, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.config_util import get_config, set_config

class AuroraConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        self.setWindowTitle("极光API配置")
        self.setFixedSize(500, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("极光API配置")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title)
        
        # 表单
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # API Key 输入框
        self.api_key = QLineEdit()
        self.api_key.setMinimumWidth(300)
        self.api_key.setFrame(False)
        self.api_key.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1e293b;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        api_key_label = QLabel("API Key:")
        api_key_label.setStyleSheet("border: none;")
        form_layout.addRow(api_key_label, self.api_key)
        
        # 模型选择
        self.model = QComboBox()
        self.model.addItems([
            "gemini-2.5-flash-lite-preview-06-17"
        ])
        self.model.setMinimumWidth(300)
        self.model.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1e293b;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #6366f1;
                border: none;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)
        model_label = QLabel("默认模型:")
        model_label.setStyleSheet("border: none;")
        form_layout.addRow(model_label, self.model)
        
        layout.addWidget(form_container)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumSize(100, 36)
        cancel_btn.setFont(QFont("Microsoft YaHei UI", 13))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.setMinimumSize(100, 36)
        save_btn.setFont(QFont("Microsoft YaHei UI", 13))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addWidget(button_container)
        
    def load_config(self):
        api_key = get_config("aicvw_apikey")
        model = get_config("aicvw_model")
        if api_key:
            self.api_key.setText(api_key)
        if model and model in [self.model.itemText(i) for i in range(self.model.count())]:
            self.model.setCurrentText(model)
            
    def save_config(self):
        set_config("aicvw_apikey", self.api_key.text())
        set_config("aicvw_model", self.model.currentText())
        self.accept()
        
    def get_config(self):
        return {
            "api_key": self.api_key.text(),
            "model": self.model.currentText()
        }