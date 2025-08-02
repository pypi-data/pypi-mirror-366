from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTextEdit, QWidget, QComboBox, QFileDialog,
                           QRadioButton, QButtonGroup, QSpinBox, QMessageBox,
                           QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.models import Task, Work
import os

class Image2VideoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt = ""
        self.image_dir = ""
        self.music_dir = ""
        self.image_files = []  # 存储图片文件列表
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("创建图生视频任务")
        self.setFixedSize(800, 600)  # 增加高度以适应新的音乐选择区域
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel {
                color: #1e293b;
            }
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 0 12px;
                background-color: #ffffff;
                color: #1e293b;
            }
            QComboBox:hover {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(:/icons/down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #f1f5f9;
                selection-color: #1e293b;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                height: 36px;
                padding-left: 12px;
                color: #1e293b;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px;
                background-color: #ffffff;
                color: #1e293b;
            }
            QTextEdit:focus {
                border-color: #6366f1;
            }
            QPushButton {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 16px;
                background-color: #ffffff;
                color: #64748b;
            }
            QPushButton:hover {
                border-color: #6366f1;
                color: #1e293b;
            }
            QPushButton#confirmBtn {
                background-color: #6366f1;
                border: none;
                color: #ffffff;
            }
            QPushButton#confirmBtn:hover {
                background-color: #4f46e5;
            }
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
            QCheckBox {
                color: #1e293b;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #e2e8f0;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border: 2px solid #6366f1;
            }
            QSpinBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 0 12px;
                background-color: #ffffff;
                color: #1e293b;
            }
            QSpinBox:hover {
                border-color: #6366f1;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
            }
            QSpinBox::up-button {
                border-top-right-radius: 6px;
                border-left: none;
                border-bottom: none;
            }
            QSpinBox::down-button {
                border-bottom-right-radius: 6px;
                border-left: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #e2e8f0;
            }
            QSpinBox::up-arrow {
                image: url(up_arrow.png);
                width: 8px;
                height: 8px;
            }
            QSpinBox::down-arrow {
                image: url(down_arrow.png);
                width: 8px;
                height: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        
        # 图片文件夹选择
        image_label = QLabel("图片文件夹")
        image_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(image_label)
        
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(16)
        
        self.image_path = QLabel("未选择图片文件夹")
        self.image_path.setFont(QFont("Microsoft YaHei UI", 13))
        self.image_path.setStyleSheet("color: #64748b;")
        image_layout.addWidget(self.image_path)
        
        select_dir_btn = QPushButton("选择文件夹")
        select_dir_btn.setFixedSize(100, 36)
        select_dir_btn.clicked.connect(self.select_image_dir)
        image_layout.addWidget(select_dir_btn)
        
        layout.addWidget(image_container)
        
        # 超级提示词
        prompt_label = QLabel("超级提示词（可选）")
        prompt_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(prompt_label)
        
        prompt_container = QWidget()
        prompt_layout = QHBoxLayout(prompt_container)
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.setSpacing(16)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setFixedHeight(100)
        prompt_layout.addWidget(self.prompt_edit)
        
        upload_btn = QPushButton("上传提示词")
        upload_btn.setFixedSize(100, 36)
        upload_btn.clicked.connect(self.upload_prompt)
        prompt_layout.addWidget(upload_btn)
        
        layout.addWidget(prompt_container)
        
        # 视频时长选择
        duration_label = QLabel("视频时长")
        duration_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(duration_label)
        
        duration_group = QButtonGroup(self)
        duration_container = QWidget()
        duration_layout = QHBoxLayout(duration_container)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        
        self.duration_5s = QRadioButton("5秒")
        self.duration_5s.setFont(QFont("Microsoft YaHei UI", 13))
        self.duration_10s = QRadioButton("10秒")
        self.duration_10s.setFont(QFont("Microsoft YaHei UI", 13))
        duration_group.addButton(self.duration_5s)
        duration_group.addButton(self.duration_10s)
        self.duration_5s.setChecked(True)
        
        duration_layout.addWidget(self.duration_5s)
        duration_layout.addWidget(self.duration_10s)
        duration_layout.addStretch()
        
        layout.addWidget(duration_container)

        # 分辨率选择
        resolution_label = QLabel("分辨率")
        resolution_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(resolution_label)

        resolution_container = QWidget()
        resolution_layout = QHBoxLayout(resolution_container)
        resolution_layout.setContentsMargins(0, 0, 0, 0)

        resolution_group = QButtonGroup(self)
        self.resolution_916 = QRadioButton("9:16")
        self.resolution_916.setFont(QFont("Microsoft YaHei UI", 13))
        self.resolution_169 = QRadioButton("16:9")
        self.resolution_169.setFont(QFont("Microsoft YaHei UI", 13))
        resolution_group.addButton(self.resolution_916)
        resolution_group.addButton(self.resolution_169)
        self.resolution_916.setChecked(True)

        resolution_layout.addWidget(self.resolution_916)
        resolution_layout.addWidget(self.resolution_169)
        resolution_layout.addStretch()

        layout.addWidget(resolution_container)
        
        # 音乐选择
        music_label = QLabel("背景音乐")
        music_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(music_label)
        
        music_container = QWidget()
        music_layout = QHBoxLayout(music_container)
        music_layout.setContentsMargins(0, 0, 0, 0)
        music_layout.setSpacing(16)
        
        self.add_music = QCheckBox("添加音乐")
        self.add_music.setFont(QFont("Microsoft YaHei UI", 13))
        music_layout.addWidget(self.add_music)
        
        self.music_path = QLabel("未选择音乐文件夹")
        self.music_path.setFont(QFont("Microsoft YaHei UI", 13))
        self.music_path.setStyleSheet("color: #64748b;")
        self.music_path.hide()
        music_layout.addWidget(self.music_path)
        
        music_layout.addStretch()
        
        select_music_btn = QPushButton("选择文件夹")
        select_music_btn.setFixedSize(100, 28)  # 修改为28像素高度，与文生视频对话框一致
        select_music_btn.clicked.connect(self.select_music_dir)
        select_music_btn.hide()
        music_layout.addWidget(select_music_btn)
        
        layout.addWidget(music_container)
        
        self.add_music.toggled.connect(lambda checked: self.music_path.setVisible(checked))
        self.add_music.toggled.connect(lambda checked: select_music_btn.setVisible(checked))
        
        layout.addStretch()
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(16)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setFont(QFont("Microsoft YaHei UI", 13))
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = QPushButton("创建任务")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setFixedSize(100, 36)
        confirm_btn.setFont(QFont("Microsoft YaHei UI", 13))
        confirm_btn.clicked.connect(self.accept_task)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)
        
        layout.addWidget(button_container)
                
    def select_image_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if dir_path:
            # 获取文件夹中的图片文件
            self.image_files = []
            for file in os.listdir(dir_path):
                # 检查文件扩展名
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    self.image_files.append(os.path.join(dir_path, file))
            
            if not self.image_files:
                QMessageBox.warning(
                    self,
                    "警告",
                    "所选文件夹中没有找到图片文件（支持 .png, .jpg, .jpeg, .webp）",
                    QMessageBox.StandardButton.Ok
                )
                return
            
            self.image_dir = dir_path
            self.image_path.setText(f"{dir_path} (找到 {len(self.image_files)} 张图片)")
            
    def select_music_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if dir_path:
            # 检查文件夹中是否有音乐文件
            music_files = []
            for file in os.listdir(dir_path):
                if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                    music_files.append(os.path.join(dir_path, file))
            
            if not music_files:
                QMessageBox.warning(
                    self,
                    "警告",
                    "所选文件夹中没有找到音乐文件（支持 .mp3, .wav, .m4a）",
                    QMessageBox.StandardButton.Ok
                )
                return
            
            self.music_dir = dir_path
            self.music_path.setText(f"{dir_path} (找到 {len(music_files)} 个音乐文件)")
            
    def upload_prompt(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择提示词文件", "", "Markdown Files (*.md)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.prompt_edit.setText(f.read())

    def accept_task(self):
        if not self.image_files:
            QMessageBox.warning(
                self,
                "警告",
                "请先选择包含图片的文件夹",
                QMessageBox.StandardButton.Ok
            )
            return
            
        if self.add_music.isChecked() and not self.music_dir:
            QMessageBox.warning(
                self,
                "警告",
                "请选择音乐文件夹",
                QMessageBox.StandardButton.Ok
            )
            return
            
        # 创建任务
        task = Task.create(
            type="image2video",
            status="pending",
            image2video="runway",
            music_dir=self.music_dir if self.add_music.isChecked() else "",
            resolution="9:16" if self.resolution_916.isChecked() else "16:9"
        )

        # 获取超级提示词
        super_prompt = self.prompt_edit.toPlainText().strip()

        # 为每张图片创建工作项
        for image_path in self.image_files:
            Work.create(
                task=task,
                image_path=image_path,
                super_prompt=super_prompt,  # 可以为空字符串
                second=5 if self.duration_5s.isChecked() else 10,
                status="pending"
            )

        self.accept() 