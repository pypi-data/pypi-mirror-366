from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QLabel, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.auth_util import pjysdk
from shiyunzi.utils.log_util import get_logger
from shiyunzi.utils.models import Config
from shiyunzi.view.main_window import MainWindow
import uuid
import os
from shiyunzi.utils.config_util import set_config, get_config
from shiyunzi.utils.log_util import pack_log_file

class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:hover {
                border-color: #6366f1;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
            QPushButton:disabled {
                background-color: #c7d2fe;
            }
        """)

class SecondaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #6366f1;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: normal;
            }
            QPushButton:hover {
                border-color: #6366f1;
                background-color: #f8fafc;
            }
        """)

class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.logger.info("登录窗口初始化")
        
        self.setWindowTitle("诗云子")
        self.setFixedSize(340, 460)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #1e293b;
            }
            QWidget {
                font-family: "Microsoft YaHei UI";
            }
        """)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(25, 65, 25, 35)
        
        # 标题区域
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel("诗云子")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Microsoft YaHei UI", 28)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1e293b; margin-top: 0px;")
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("智能创作助手")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Microsoft YaHei UI", 14))
        subtitle_label.setStyleSheet("color: #64748b;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_container)
        layout.addSpacing(30)
        
        # 输入区域
        input_label = QLabel("授权码")
        input_label.setFont(QFont("Microsoft YaHei UI", 13))
        input_label.setStyleSheet("color: #475569;")
        layout.addWidget(input_label)
        
        self.license_input = CustomLineEdit()
        self.license_input.setPlaceholderText("请输入授权码")
        self.license_input.setMinimumHeight(42)
        self.license_input.setFont(QFont("Microsoft YaHei UI", 13))
        
        # 获取保存的授权码
        saved_card = get_config("card")
        if saved_card:
            self.license_input.setText(saved_card)
            
        layout.addWidget(self.license_input)
        
        layout.addSpacing(20)
        
        # 登录按钮
        self.login_button = PrimaryButton("登录")
        self.login_button.setMinimumHeight(42)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.verify_license)
        layout.addWidget(self.login_button)
        
        layout.addSpacing(10)
        
        # 底部按钮区域
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setSpacing(10)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 打包日志按钮
        self.log_button = SecondaryButton("打包日志")
        self.log_button.setMinimumHeight(38)
        self.log_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.log_button.clicked.connect(pack_log_file)
        bottom_layout.addWidget(self.log_button)
        
        # 试用登录按钮
        self.buy_button = SecondaryButton("试用登录")
        self.buy_button.setMinimumHeight(38)
        self.buy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        bottom_layout.addWidget(self.buy_button)
        self.buy_button.clicked.connect(self.trial_login)
        
        layout.addWidget(bottom_container)
        
        # 添加联系方式
        contact_label = QLabel("遇到问题？请联系微信：tkshuke")
        contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_label.setStyleSheet("color: #64748b; font-size: 12px; margin-top: 5px;")
        layout.addWidget(contact_label)
        
    def verify_license(self):
        self.login_button.setEnabled(False)
        self.login_button.setText("验证中...")
        
        license_key = self.license_input.text().strip()
        if not license_key:
            self.logger.warning("用户未输入授权码")
            QMessageBox.warning(self, "提示", "请输入授权码")
            self.login_button.setEnabled(True)
            self.login_button.setText("登录")
            return
            
        # 验证授权码
        self.logger.info("开始验证授权码")
        pjysdk.set_device_id(get_config("device_id"))
        pjysdk.set_card(license_key)
        result = pjysdk.card_login()
        if result.code == 0:
            self.logger.info("授权码验证成功")
            expires = result.result.expires
            QMessageBox.information(self, "授权成功", f"您的授权将在 {expires} 到期")
            
            # 保存授权码
            set_config("card", license_key)
            
            # 打开主窗口
            self.main_window = MainWindow()
            self.main_window.show()
            self.hide()
        else:
            self.logger.error("授权码验证失败")
            QMessageBox.warning(self, "验证失败", "授权码无效或已过期")
        
        self.login_button.setEnabled(True)
        self.login_button.setText("登录")
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.verify_license()
            
    def closeEvent(self, event):
        # 接受关闭事件
        event.accept()
        # 强制退出程序
        os._exit(0) 
    
    # 试用登录函数
    def trial_login(self):
        self.buy_button.setEnabled(False)
        pjysdk.set_device_id(get_config("device_id"))
        result = pjysdk.trial_login()
        
        if result.code == 0:
            self.logger.info("试用授权码验证成功")
            expires = result.result.expires
            QMessageBox.information(self, "授权成功", f"您的试用授权将在 {expires} 到期")
            
            # 打开主窗口
            self.main_window = MainWindow()
            self.main_window.show()
            self.hide()
        else:
            self.logger.error("试用通知")
            QMessageBox.warning(self, "验证失败", "您已经试用过了,请购买授权")
        