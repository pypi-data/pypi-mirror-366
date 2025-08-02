from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QWidget, QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.models import RunwayAccount
from runwayapi import get_user_team_id

class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
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

class CustomRadioButton(QRadioButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QRadioButton {
                color: #1e293b;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 9px;
                background-color: #ffffff;
            }
            QRadioButton::indicator:hover {
                border-color: #6366f1;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #6366f1;
                background-color: #6366f1;
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
                padding: 8px 12px;
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
                padding: 8px 12px;
                font-size: 13px;
                font-weight: normal;
            }
            QPushButton:hover {
                border-color: #6366f1;
                background-color: #f8fafc;
            }
        """)

class RunwayDialog(QDialog):
    def __init__(self, account=None, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("添加配置" if not account else "编辑配置")
        self.setFixedSize(400, 290)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #475569;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 店铺名称
        name_label = QLabel("店铺名称")
        name_label.setStyleSheet("border: none;")
        name_label.setFont(QFont("Microsoft YaHei UI", 13))
        layout.addWidget(name_label)
        
        self.name_input = CustomLineEdit()
        self.name_input.setPlaceholderText("请输入店铺名称")
        self.name_input.setMinimumHeight(36)
        self.name_input.setFont(QFont("Microsoft YaHei UI", 13))
        if self.account:
            self.name_input.setText(self.account.name)
        layout.addWidget(self.name_input)
        
        # Token
        token_label = QLabel("TOKEN")
        token_label.setStyleSheet("border: none;")
        token_label.setFont(QFont("Microsoft YaHei UI", 13))
        layout.addWidget(token_label)
        
        self.token_input = CustomLineEdit()
        self.token_input.setPlaceholderText("请输入TOKEN")
        self.token_input.setMinimumHeight(36)
        self.token_input.setFont(QFont("Microsoft YaHei UI", 13))
        if self.account:
            self.token_input.setText(self.account.token)
        layout.addWidget(self.token_input)
        
        # 账号类型
        type_label = QLabel("账号类型")
        type_label.setStyleSheet("border: none;")
        type_label.setFont(QFont("Microsoft YaHei UI", 13))
        layout.addWidget(type_label)
        
        type_container = QWidget()
        type_layout = QHBoxLayout(type_container)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(20)
        
        self.type_group = QButtonGroup(self)
        
        shared_radio = CustomRadioButton("共享账号")
        shared_radio.setStyleSheet("border: none;")
        exclusive_radio = CustomRadioButton("独享账号")
        exclusive_radio.setStyleSheet("border: none;")
        
        self.type_group.addButton(shared_radio)
        self.type_group.addButton(exclusive_radio)
        
        type_layout.addWidget(shared_radio)
        type_layout.addWidget(exclusive_radio)
        type_layout.addStretch()
        
        if self.account:
            shared_radio.setChecked(self.account.type == "shared")
            exclusive_radio.setChecked(self.account.type == "exclusive")
        else:
            shared_radio.setChecked(True)
            
        layout.addWidget(type_container)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        cancel_btn = SecondaryButton("取消")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        confirm_btn = PrimaryButton("确定")
        confirm_btn.setMinimumHeight(36)
        confirm_btn.clicked.connect(self.save_account)
        button_layout.addWidget(confirm_btn)
        
        layout.addWidget(button_container)
        
    def save_account(self):
        name = self.name_input.text().strip()
        token = self.token_input.text().strip()
        account_type = "shared" if self.type_group.checkedButton().text() == "共享账号" else "exclusive"
        
        # 调用获取team_id
        team_id = get_user_team_id(token)
        if team_id == 401:
            QMessageBox.warning(self, "提示", "TOKEN已过期")
            return
        if team_id == None:
            QMessageBox.warning(self, "提示", "TOKEN无效")
            return

        if not all([name, token]):
            return
            
        if self.account:
            # 更新现有账号
            self.account.name = name
            self.account.token = token
            self.account.type = account_type
            self.account.team_id = team_id
            self.account.save()
        else:
            # 创建新账号
            RunwayAccount.create(
                name=name,
                token=token,
                team_id=team_id,
                used=0,
                status=0,
                type=account_type
            )
            
        self.accept() 