from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QLineEdit,
                           QFormLayout, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.config_util import get_config, set_config

class SDConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        self.setWindowTitle("Stable Diffusion 配置")
        self.setFixedSize(500, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("Stable Diffusion 配置")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title)
        
        # 表单
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 服务器地址输入框
        self.server = QLineEdit()
        self.server.setMinimumWidth(300)
        self.server.setPlaceholderText("例如：http://localhost:7860")
        self.server.setStyleSheet("""
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
        server_label = QLabel("服务器地址:")
        server_label.setStyleSheet("border: none;")
        form_layout.addRow(server_label, self.server)
        
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
        sd_server = get_config("sd_server")
        if sd_server:
            self.server.setText(sd_server)
            
    def save_config(self):
        server = self.server.text().strip()
        if server:
            set_config("sd_server", server)
            self.accept()
        else:
            self.reject() 