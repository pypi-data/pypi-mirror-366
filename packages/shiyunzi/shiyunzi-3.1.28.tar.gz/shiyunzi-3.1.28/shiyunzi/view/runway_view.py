from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from shiyunzi.utils.models import RunwayAccount
from shiyunzi.view.runway_dialog import RunwayDialog

class AccountTypeLabel(QLabel):
    def __init__(self, text, type_style="shared", parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if type_style == "shared":
            bg_color = "#dbeafe"
            text_color = "#2563eb"
        else:  # exclusive
            bg_color = "#dcfce7"
            text_color = "#16a34a"
            
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 4px;
                padding: 4px 12px;
            }}
        """)
        self.setFixedWidth(80)

class ActionButton(QPushButton):
    def __init__(self, text, is_delete=False, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        color = "#ef4444" if is_delete else "#6366f1"
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {color};
                padding: 4px 8px;
                font-size: 13px;
                background: transparent;
            }}
            QPushButton:hover {{
                color: {"#dc2626" if is_delete else "#4f46e5"};
            }}
        """)

class TruncatedLabel(QLabel):
    def __init__(self, text, max_width=None, parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.max_width = max_width
        self.setFont(QFont("Microsoft YaHei UI", 13))
        
    def setText(self, text):
        self.full_text = text
        self._update_text()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_text()
        
    def _update_text(self):
        if not self.max_width:
            self.max_width = self.width()
            
        metrics = QFontMetrics(self.font())
        text = self.full_text
        
        if metrics.horizontalAdvance(text) > self.max_width:
            # 计算省略号的宽度
            ellipsis = "..."
            ellipsis_width = metrics.horizontalAdvance(ellipsis)
            
            # 逐个字符尝试，直到找到合适的长度
            i = len(text)
            while i > 0:
                truncated = text[:i]
                if metrics.horizontalAdvance(truncated + ellipsis) <= self.max_width:
                    text = truncated + ellipsis
                    break
                i -= 1
                
        super().setText(text)

class StatusLabel(QLabel):
    def __init__(self, status, parent=None):
        text = "正常" if status == 0 else "异常"
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if status == 0:  # 正常
            bg_color = "#dcfce7"
            text_color = "#16a34a"
        else:  # 异常
            bg_color = "#fee2e2"
            text_color = "#dc2626"
            
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 4px;
                padding: 4px 12px;
            }}
        """)
        self.setFixedWidth(80)

class RunwayItem(QWidget):
    def __init__(self, account, parent=None):
        super().__init__(parent)
        self.account = account
        self.parent_view = parent
        
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(0)
        
        # 店铺名称
        shop_label = TruncatedLabel(account.name)
        shop_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(shop_label, 3)
        
        # 账号类型
        type_label = AccountTypeLabel("共享" if account.type == "shared" else "独享",
                                   "shared" if account.type == "shared" else "exclusive")
        type_label.setStyleSheet("border: none;")
        layout.addWidget(type_label, 1, Qt.AlignmentFlag.AlignCenter)

        # 账号状态
        status_label = StatusLabel(account.status)
        status_label.setStyleSheet("border: none;")
        layout.addWidget(status_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # 操作按钮
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(16)
        
        edit_btn = ActionButton("编辑")
        edit_btn.clicked.connect(self.edit_account)
        delete_btn = ActionButton("删除", is_delete=True)
        delete_btn.clicked.connect(self.delete_account)
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        layout.addWidget(actions, 1)
        
    def edit_account(self):
        dialog = RunwayDialog(self.account, self)
        if dialog.exec():
            self.parent_view.load_accounts()
            
    def delete_account(self):
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 {self.account.name} 的配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.account.delete_instance()
            self.parent_view.load_accounts()

class RunwayView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_accounts()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面标题和添加按钮
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        page_title = QLabel("Runway 配置管理")
        page_title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        page_title.setStyleSheet("color: #1e293b;")
        header_layout.addWidget(page_title)
        
        add_btn = QPushButton("+ 添加配置")
        add_btn.setFont(QFont("Microsoft YaHei UI", 13))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        add_btn.clicked.connect(self.add_account)
        header_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)
        
        # 表格容器
        self.table_container = QWidget()
        self.table_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setSpacing(0)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格标题
        table_header = QWidget()
        table_header.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(24, 16, 24, 16)
        table_header_layout.setSpacing(0)
        
        headers = ["店铺名称", "账号类型", "状态", "操作"]
        widths = [3, 1, 1, 1]
        alignments = [Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter]
        
        for header_text, width, alignment in zip(headers, widths, alignments):
            label = QLabel(header_text)
            label.setFont(QFont("Microsoft YaHei UI", 13))
            label.setStyleSheet("color: #64748b; border: none;")
            label.setAlignment(alignment)
            table_header_layout.addWidget(label, width)
        table_layout.addWidget(table_header)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 6px;
                margin: 4px 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 创建一个容器来包裹内容
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置对齐方式为顶部对齐
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置对齐方式为顶部对齐
        
        content_layout.addWidget(self.scroll_content)
        scroll.setWidget(content_container)
        table_layout.addWidget(scroll)
        
        layout.addWidget(self.table_container)
        
    def load_accounts(self):
        # 清除现有内容
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # 加载账号数据
        accounts = RunwayAccount.select().order_by(RunwayAccount.created_at.desc())
        
        for i, account in enumerate(accounts):
            if i > 0:  # 在每个项目之前添加分割线（除了第一个）
                separator = QWidget()
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: #e2e8f0;")
                self.scroll_layout.addWidget(separator)
            item = RunwayItem(account, self)
            self.scroll_layout.addWidget(item)
            
    def add_account(self):
        dialog = RunwayDialog(parent=self)
        if dialog.exec():
            self.load_accounts() 