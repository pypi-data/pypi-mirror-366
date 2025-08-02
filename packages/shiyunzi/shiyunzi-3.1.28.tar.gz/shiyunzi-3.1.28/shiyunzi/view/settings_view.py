from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                            QPushButton, QFrame, QRadioButton, QButtonGroup)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import webbrowser
import os
from shiyunzi.utils.log_util import pack_log_file
from shiyunzi.utils.config_util import get_config, set_config

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'Microsoft YaHei UI';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        self.setContentsMargins(16, 16, 16, 16)

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def open_tutorial(self):
        webbrowser.open('https://h6vw7qmfq7.feishu.cn/drive/folder/PoxMftHHflfAeldivq3cd8slnAU?from=from_copylink')
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 顶部容器
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题和版本号
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b;")
        title_layout.addWidget(title)
        
        version = QLabel("v3.1.28")
        version.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        version.setStyleSheet("color: #2563eb;")
        title_layout.addWidget(version)
        
        top_layout.addWidget(title_container)
        top_layout.addStretch()
        
        # 按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        # 使用教程按钮
        tutorial_btn = PrimaryButton("使用教程")
        tutorial_btn.setFixedWidth(120)
        tutorial_btn.clicked.connect(self.open_tutorial)
        button_layout.addWidget(tutorial_btn)
        
        # 打包日志按钮
        pack_log_btn = PrimaryButton("打包日志")
        pack_log_btn.setFixedWidth(120)
        pack_log_btn.clicked.connect(lambda: pack_log_file())
        button_layout.addWidget(pack_log_btn)
        
        top_layout.addWidget(button_container)
        layout.addWidget(top_container)
        
        # 更新内容卡片
        update_card = Card()
        update_layout = QVBoxLayout(update_card)
        
        update_title = QLabel("更新内容")
        update_title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        update_title.setStyleSheet("color: #1e293b; border: none;")
        update_layout.addWidget(update_title)
        
        updates = [
            "1. 优化界面",
            "2. 优化日志打包",
            "3. 优化视频生成流程", 
            "4. 添加线上更新",
            "5. 添加StableDiffusion服务地址配置",
            "6. 文生图功能",
            "7. 图生视频功能",
            "8. 添加豆包AI平台支持"
        ]
        
        for update in updates:
            item = QLabel(update)
            item.setFont(QFont("Microsoft YaHei UI", 12))
            item.setStyleSheet("color: #475569; margin-left: 20px; border: none;")
            update_layout.addWidget(item)
            
        layout.addWidget(update_card)
        
        # 配置卡片
        config_card = Card()
        config_layout = QVBoxLayout(config_card)
        
        config_title = QLabel("配置")
        config_title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        config_title.setStyleSheet("color: #1e293b; border: none;")
        config_layout.addWidget(config_title)
        
        # Runway视频模型配置
        runway_label = QLabel("Runway视频模型")
        runway_label.setFont(QFont("Microsoft YaHei UI", 14))
        runway_label.setStyleSheet("color: #1e293b; margin-left: 20px; border: none;")
        config_layout.addWidget(runway_label)
        
        # Runway单选按钮组
        runway_group = QButtonGroup(self)
        runway_container = QWidget()
        runway_layout = QHBoxLayout(runway_container)
        runway_layout.setContentsMargins(40, 0, 0, 0)
        
        gen3_radio = QRadioButton("gen3")
        gen3_radio.setFont(QFont("Microsoft YaHei UI", 12))
        gen4_radio = QRadioButton("gen4")
        gen4_radio.setFont(QFont("Microsoft YaHei UI", 12))
        
        # 设置样式
        radio_style = """
            QRadioButton {
                color: #1e293b;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #e2e8f0;
                background-color: #ffffff;
            }
            QRadioButton::indicator:checked {
                background-color: #6366f1;
                border: 2px solid #6366f1;
            }
        """
        gen3_radio.setStyleSheet(radio_style)
        gen4_radio.setStyleSheet(radio_style)
        
        runway_group.addButton(gen3_radio)
        runway_group.addButton(gen4_radio)
        runway_layout.addWidget(gen3_radio)
        runway_layout.addWidget(gen4_radio)
        runway_layout.addStretch()
        
        config_layout.addWidget(runway_container)
        
        # 语言模型配置
        llm_label = QLabel("语言模型")
        llm_label.setFont(QFont("Microsoft YaHei UI", 14))
        llm_label.setStyleSheet("color: #1e293b; margin-left: 20px; border: none;")
        config_layout.addWidget(llm_label)
        
        # 语言模型单选按钮组
        llm_group = QButtonGroup(self)
        llm_container = QWidget()
        llm_layout = QHBoxLayout(llm_container)
        llm_layout.setContentsMargins(40, 0, 0, 0)
        
        aurora_radio = QRadioButton("极光API")
        aurora_radio.setFont(QFont("Microsoft YaHei UI", 12))
        doubao_radio = QRadioButton("豆包")
        doubao_radio.setFont(QFont("Microsoft YaHei UI", 12))
        
        aurora_radio.setStyleSheet(radio_style)
        doubao_radio.setStyleSheet(radio_style)
        
        llm_group.addButton(aurora_radio)
        llm_group.addButton(doubao_radio)
        llm_layout.addWidget(aurora_radio)
        llm_layout.addWidget(doubao_radio)
        llm_layout.addStretch()
        
        config_layout.addWidget(llm_container)
        
        # 变态模式配置
        pervert_label = QLabel("变态模式")
        pervert_label.setFont(QFont("Microsoft YaHei UI", 14))
        pervert_label.setStyleSheet("color: #1e293b; margin-left: 20px; border: none;")
        config_layout.addWidget(pervert_label)
        
        # 变态模式开关按钮组
        pervert_container = QWidget()
        pervert_layout = QHBoxLayout(pervert_container)
        pervert_layout.setContentsMargins(40, 0, 0, 0)
        
        pervert_group = QButtonGroup(self)
        pervert_on = QRadioButton("开启")
        pervert_on.setFont(QFont("Microsoft YaHei UI", 12))
        pervert_off = QRadioButton("关闭")
        pervert_off.setFont(QFont("Microsoft YaHei UI", 12))
        
        pervert_on.setStyleSheet(radio_style)
        pervert_off.setStyleSheet(radio_style)
        
        pervert_layout.addWidget(pervert_on)
        pervert_layout.addWidget(pervert_off)
        pervert_group.addButton(pervert_on)
        pervert_group.addButton(pervert_off)
        pervert_layout.addStretch()
        
        config_layout.addWidget(pervert_container)
        
        # 加载已保存的配置
        saved_runway = get_config("runway_model") or "gen3"
        saved_llm = get_config("llm_model") or "aurora"
        saved_pervert = get_config("pervert_mode") or "0"  # 默认关闭
        
        if saved_runway == "gen3":
            gen3_radio.setChecked(True)
        else:
            gen4_radio.setChecked(True)
            
        if saved_llm == "aurora":
            aurora_radio.setChecked(True)
        else:
            doubao_radio.setChecked(True)
            
        if saved_pervert == "1":
            pervert_on.setChecked(True)
        else:
            pervert_off.setChecked(True)
        
        # 保存配置的槽函数
        def save_runway_config():
            model = "gen3" if gen3_radio.isChecked() else "gen4"
            set_config("runway_model", model)
            
        def save_llm_config():
            model = "aurora" if aurora_radio.isChecked() else "doubao"
            set_config("llm_model", model)
            
        def save_pervert_config():
            mode = "1" if pervert_on.isChecked() else "0"
            set_config("pervert_mode", mode)
        
        # 连接信号
        runway_group.buttonClicked.connect(save_runway_config)
        llm_group.buttonClicked.connect(save_llm_config)
        pervert_group.buttonClicked.connect(save_pervert_config)
        
        layout.addWidget(config_card)
        layout.addStretch()