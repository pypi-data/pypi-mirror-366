from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.view.runway_view import RunwayView
from shiyunzi.view.settings_view import SettingsView
from shiyunzi.view.ai_view import AIView
from shiyunzi.view.sd_view import SDView
from shiyunzi.view.video_view import VideoView
from shiyunzi.view.text2video_view import Text2VideoView
from shiyunzi.view.text2image_view import Text2ImageView
from shiyunzi.view.image2video_view import Image2VideoView
from shiyunzi.view.product_video_view import ProductVideoView
from shiyunzi.view.sticker_view import StickerView
import os

class DrawerButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 16px;
                border: none;
                border-radius: 6px;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
            QPushButton:checked {
                background-color: #eff6ff;
                color: #6366f1;
            }
        """)

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

class IconButton(QPushButton):
    def __init__(self, icon_text, color="#6366f1", parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei UI", 16))
        self.setText(icon_text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: {color};
                padding: 4px 8px;
                background: transparent;
            }}
            QPushButton:hover {{
                color: {color if color == "#ef4444" else "#4f46e5"};
            }}
        """)

class RunwayItem(QWidget):
    def __init__(self, shop_name, token, account_type, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QWidget:hover {
                border-color: #cbd5e1;
                background-color: #fafafa;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 店铺名称
        shop_label = QLabel(shop_name)
        shop_label.setFont(QFont("Microsoft YaHei UI", 14))
        shop_label.setStyleSheet("color: #1e293b; font-weight: 500;")
        layout.addWidget(shop_label, 2)
        
        # Token
        token_label = QLabel(token)
        token_label.setFont(QFont("Microsoft YaHei UI", 13))
        token_label.setStyleSheet("color: #64748b;")
        layout.addWidget(token_label, 3)
        
        # 账号类型
        type_label = AccountTypeLabel("共享" if account_type == "shared" else "独享",
                                   "shared" if account_type == "shared" else "exclusive")
        layout.addWidget(type_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # 操作按钮
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(16)
        
        edit_btn = IconButton("✎")  # 编辑图标
        delete_btn = IconButton("🗑", "#ef4444")  # 删除图标
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        layout.addWidget(actions, 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("诗云子")
        self.resize(1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建水平布局
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建左侧抽屉
        drawer = QWidget()
        drawer.setFixedWidth(220)
        drawer.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
        """)
        drawer_layout = QVBoxLayout(drawer)
        drawer_layout.setContentsMargins(20, 24, 20, 24)
        drawer_layout.setSpacing(4)
        
        # 添加标题
        title_label = QLabel("诗云子")
        title_label.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #6366f1; margin-bottom: 2px;")
        drawer_layout.addWidget(title_label)
        
        subtitle_label = QLabel("智能创作平台")
        subtitle_label.setFont(QFont("Microsoft YaHei UI", 13))
        subtitle_label.setStyleSheet("color: #64748b; margin-bottom: 32px;")
        drawer_layout.addWidget(subtitle_label)
        
        
        # 添加导航按钮
        self.text2image_btn = DrawerButton("文生图")
        self.text2image_btn.clicked.connect(lambda: self.switch_page(0))
        drawer_layout.addWidget(self.text2image_btn)

        self.text2video_btn = DrawerButton("文生视频")
        self.text2video_btn.clicked.connect(lambda: self.switch_page(1))
        drawer_layout.addWidget(self.text2video_btn)

        self.image2video_btn = DrawerButton("图生视频")
        self.image2video_btn.clicked.connect(lambda: self.switch_page(2))
        drawer_layout.addWidget(self.image2video_btn)

        self.product_video_btn = DrawerButton("带货视频")
        self.product_video_btn.clicked.connect(lambda: self.switch_page(3))
        drawer_layout.addWidget(self.product_video_btn)

        self.sticker_btn = DrawerButton("贴纸功能")
        self.sticker_btn.clicked.connect(lambda: self.switch_page(4))
        drawer_layout.addWidget(self.sticker_btn)

        self.runway_btn = DrawerButton("Runway 配置")
        self.runway_btn.clicked.connect(lambda: self.switch_page(5))
        drawer_layout.addWidget(self.runway_btn)
        
        self.ai_btn = DrawerButton("AI 配置")
        self.ai_btn.clicked.connect(lambda: self.switch_page(6))
        drawer_layout.addWidget(self.ai_btn)
        
        self.sd_btn = DrawerButton("Stable Diffusion")
        self.sd_btn.clicked.connect(lambda: self.switch_page(7))
        drawer_layout.addWidget(self.sd_btn)
        
        self.video_btn = DrawerButton("视频解析")
        self.video_btn.clicked.connect(lambda: self.switch_page(8))
        drawer_layout.addWidget(self.video_btn)
        
        self.settings_btn = DrawerButton("设置")
        self.settings_btn.clicked.connect(lambda: self.switch_page(9))
        drawer_layout.addWidget(self.settings_btn)
        
        drawer_layout.addStretch()
        layout.addWidget(drawer)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 32, 32, 32)
        
        # 创建堆叠窗口部件用于切换页面
        self.stack = QStackedWidget()

        # 添加文生图页面
        self.text2image_view = Text2ImageView()
        self.stack.addWidget(self.text2image_view)

        # 添加文生视频页面
        self.text2video_view = Text2VideoView()
        self.stack.addWidget(self.text2video_view)

        # 添加图生视频页面
        self.image2video_view = Image2VideoView()
        self.stack.addWidget(self.image2video_view)

        # 添加带货视频页面
        self.product_video_view = ProductVideoView()
        self.stack.addWidget(self.product_video_view)
        
        # 添加贴纸功能页面
        self.sticker_view = StickerView()
        self.stack.addWidget(self.sticker_view)
        
        # 添加 Runway 配置页面
        self.runway_view = RunwayView()
        self.stack.addWidget(self.runway_view)
        
        # 添加 AI 配置页面
        self.ai_view = AIView()
        self.stack.addWidget(self.ai_view)
        
        # 添加 SD 配置页面
        self.sd_view = SDView()
        self.stack.addWidget(self.sd_view)
        
        # 添加视频解析页面
        self.video_view = VideoView()
        self.stack.addWidget(self.video_view)
        
        # 添加设置页面
        self.settings_view = SettingsView()
        self.stack.addWidget(self.settings_view)
        
        content_layout.addWidget(self.stack)
        layout.addWidget(content_widget)

        # 默认选择第一个页面
        self.switch_page(0)
        
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        # 更新按钮状态
        self.text2image_btn.setChecked(index == 0)
        self.text2video_btn.setChecked(index == 1)
        self.image2video_btn.setChecked(index == 2)
        self.product_video_btn.setChecked(index == 3)
        self.sticker_btn.setChecked(index == 4)
        self.runway_btn.setChecked(index == 5)
        self.ai_btn.setChecked(index == 6)
        self.sd_btn.setChecked(index == 7)
        self.video_btn.setChecked(index == 8)
        self.settings_btn.setChecked(index == 9)
        
    def closeEvent(self, event):
        # 接受关闭事件
        event.accept()
        # 强制退出程序
        os._exit(0) 