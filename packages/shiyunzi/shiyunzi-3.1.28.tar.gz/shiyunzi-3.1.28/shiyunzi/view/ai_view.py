from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QPushButton, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
import os
from .aurora_config_dialog import AuroraConfigDialog
from .sd_config_dialog import SDConfigDialog
from .doubao_config_dialog import DoubaoConfigDialog
from shiyunzi.utils.config_util import get_config, set_config

class AICard(QFrame):
    configChanged = pyqtSignal()  # 信号：配置已更改
    
    def __init__(self, title, config_dialog_class, config_key, is_configured=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.config_dialog_class = config_dialog_class
        self.config_key = config_key
        self.setup_ui(title, is_configured)
        
    def setup_ui(self, title, is_configured):
        self.setFixedSize(360, 80)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #6366f1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 标题和状态行
        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # 左侧容器（图标和标题）
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet("border: none;")
        
        # 加载 SVG 图标
        svg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "robot.svg")
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        icon_label.setPixmap(pixmap)
        left_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #1e293b; border: none;")
        left_layout.addWidget(title_label)
        
        title_layout.addWidget(left_container)
        
        # 状态标签（靠右）
        self.status_label = QLabel("已配置" if is_configured else "未配置")
        self.status_label.setStyleSheet(self._get_status_style(is_configured))
        self.status_label.setFixedHeight(20)
        self.status_label.setContentsMargins(8, 2, 8, 2)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {('#10b981' if is_configured else '#94a3b8')};
                font-size: 12px;
                background: {('#f0fdf4' if is_configured else '#f1f5f9')};
                border: 1px solid {('#86efac' if is_configured else '#e2e8f0')};
                border-radius: 4px;
                padding: 0 8px;
            }}
        """)
        title_layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(title_row)
        
        # 描述文本
        desc_label = QLabel(f"配置 {title} API 密钥和相关参数")
        desc_label.setFont(QFont("Microsoft YaHei UI", 12))
        desc_label.setStyleSheet("color: #64748b;  border: none;")
        layout.addWidget(desc_label)
        
    def _get_status_style(self, is_configured):
        return f"""
            QLabel {{
                color: {'#10b981' if is_configured else '#94a3b8'};
                font-size: 12px;
            }}
        """
        
    def set_configured(self, is_configured):
        self.status_label.setText("已配置" if is_configured else "未配置")
        self.status_label.setStyleSheet(self._get_status_style(is_configured))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = self.config_dialog_class(self)
            if dialog.exec() == self.config_dialog_class.DialogCode.Accepted:
                self.configChanged.emit()

class AIView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("AI 配置管理")
        title.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # 卡片容器
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(24)
        
        # 第一行容器
        row1_container = QWidget()
        row1_layout = QHBoxLayout(row1_container)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(24)
        
        # 添加极光API卡片
        aicvw_apikey = get_config("aicvw_apikey")
        self.aurora_card = AICard("极光API站", AuroraConfigDialog, "aicvw_apikey", bool(aicvw_apikey))
        self.aurora_card.configChanged.connect(self.on_aurora_config_changed)
        row1_layout.addWidget(self.aurora_card)
        
        # 添加 SD 卡片
        sd_server = get_config("sd_server")
        self.sd_card = AICard("Stable Diffusion", SDConfigDialog, "sd_server", bool(sd_server))
        self.sd_card.configChanged.connect(self.on_sd_config_changed)
        row1_layout.addWidget(self.sd_card)
        
        row1_layout.addStretch()
        cards_layout.addWidget(row1_container)
        
        # 第二行容器
        row2_container = QWidget()
        row2_layout = QHBoxLayout(row2_container)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(24)
        
        # 添加豆包卡片
        doubao_cookie = get_config("doubao_cookie")
        self.doubao_card = AICard("豆包API", DoubaoConfigDialog, "doubao_cookie", bool(doubao_cookie))
        self.doubao_card.configChanged.connect(self.on_doubao_config_changed)
        row2_layout.addWidget(self.doubao_card)
        
        row2_layout.addStretch()
        cards_layout.addWidget(row2_container)
        
        cards_layout.addStretch()
        
        # 使用滚动区域包装卡片容器
        scroll = QScrollArea()
        scroll.setWidget(cards_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background-color: #f1f5f9;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(scroll)
        layout.addStretch()
        
    def on_aurora_config_changed(self):
        aicvw_apikey = get_config("aicvw_apikey")
        self.aurora_card.set_configured(bool(aicvw_apikey))
        
    def on_sd_config_changed(self):
        sd_server = get_config("sd_server")
        self.sd_card.set_configured(bool(sd_server))
        
    def on_doubao_config_changed(self):
        doubao_cookie = get_config("doubao_cookie")
        self.doubao_card.set_configured(bool(doubao_cookie))