from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTextEdit, QWidget, QComboBox, QFileDialog,
                           QRadioButton, QButtonGroup, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.models import StableDiffusion, Task, Work

class Text2ImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("创建文生图任务")
        self.setFixedSize(800, 600)
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
        
        # 文生图模型选择
        text2image_label = QLabel("文生图模型")
        text2image_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(text2image_label)
        
        text2image_container = QWidget()
        text2image_layout = QHBoxLayout(text2image_container)
        text2image_layout.setContentsMargins(0, 0, 0, 0)
        
        text2image_group = QButtonGroup(self)
        self.runway_radio = QRadioButton("Runway")
        self.runway_radio.setFont(QFont("Microsoft YaHei UI", 13))
        self.sd_radio = QRadioButton("Stable Diffusion")
        self.sd_radio.setFont(QFont("Microsoft YaHei UI", 13))
        self.doubao_radio = QRadioButton("豆包")
        self.doubao_radio.setFont(QFont("Microsoft YaHei UI", 13))
        text2image_group.addButton(self.runway_radio)
        text2image_group.addButton(self.sd_radio)
        text2image_group.addButton(self.doubao_radio)
        self.runway_radio.setChecked(True)
        
        text2image_layout.addWidget(self.runway_radio)
        text2image_layout.addWidget(self.sd_radio)
        text2image_layout.addWidget(self.doubao_radio)
        text2image_layout.addStretch()
        
        layout.addWidget(text2image_container)
        
        # Stable Diffusion配置选择
        self.sd_config_container = QWidget()
        sd_config_layout = QHBoxLayout(self.sd_config_container)
        sd_config_layout.setContentsMargins(0, 0, 0, 0)
        
        sd_config_label = QLabel("Stable配置")
        sd_config_label.setFont(QFont("Microsoft YaHei UI", 13))
        sd_config_layout.addWidget(sd_config_label)
        
        self.sd_config_combo = QComboBox()
        self.sd_config_combo.addItems([sd.name for sd in StableDiffusion.select()])
        self.sd_config_combo.setFixedHeight(36)
        sd_config_layout.addWidget(self.sd_config_combo)
        sd_config_layout.addStretch()
        
        layout.addWidget(self.sd_config_container)
        self.sd_config_container.hide()
        
        # 超级提示词
        prompt_label = QLabel("超级提示词")
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

        # 生成数量选择
        count_label = QLabel("生成数量")
        count_label.setFont(QFont("Microsoft YaHei UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(count_label)

        count_container = QWidget()
        count_layout = QHBoxLayout(count_container)
        count_layout.setContentsMargins(0, 0, 0, 0)

        self.count_spinbox = QSpinBox()
        self.count_spinbox.setFixedSize(100, 36)
        self.count_spinbox.setFont(QFont("Microsoft YaHei UI", 13))
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(1)
        count_layout.addWidget(self.count_spinbox)
        count_layout.addStretch()

        layout.addWidget(count_container)
        
        layout.addStretch()
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(16)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFont(QFont("Microsoft YaHei UI", 13))
        cancel_btn.clicked.connect(self.reject)
        
        batch_create_btn = QPushButton("批量创建")
        batch_create_btn.setFixedSize(100, 36)
        batch_create_btn.setFont(QFont("Microsoft YaHei UI", 13))
        batch_create_btn.clicked.connect(self.batch_create_tasks)
        
        confirm_btn = QPushButton("创建任务")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setFixedSize(100, 36)
        confirm_btn.setFont(QFont("Microsoft YaHei UI", 13))
        confirm_btn.clicked.connect(self.accept_task)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(batch_create_btn)
        button_layout.addWidget(confirm_btn)
        
        layout.addWidget(button_container)
        
        # 连接信号
        self.sd_radio.toggled.connect(self.sd_config_container.setVisible)
        
    def upload_prompt(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择提示词文件", "", "Markdown Files (*.md)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.prompt_edit.setText(f.read())
                
    def accept_task(self):
        self.prompt = self.prompt_edit.toPlainText().strip()
        if not self.prompt:
            return
            
        # 创建任务
        text2image = "runway"
        if self.sd_radio.isChecked():
            text2image = "sd"
        elif self.doubao_radio.isChecked():
            text2image = "doubao"
            
        task = Task.create(
            type="text2image",
            status="pending",
            text2image=text2image,
            resolution="9:16" if self.resolution_916.isChecked() else "16:9"
        )

        if self.sd_radio.isChecked():
            stable_diffusion = StableDiffusion.select().where(StableDiffusion.name == self.sd_config_combo.currentText()).first()
        else:
            stable_diffusion = None

        # 创建工作项
        for _ in range(self.count_spinbox.value()):
            Work.create(
                task=task,
                super_prompt=self.prompt,
                stable_diffusion=stable_diffusion,
                status="pending"
            )

        self.accept() 

    def batch_create_tasks(self):
        prompts = self.prompt_edit.toPlainText().strip().split('\n')
        if not prompts:
            return
            
        for prompt in prompts:
            prompt = prompt.strip()
            if not prompt:
                continue
                
            # 创建任务
            text2image = "runway"
            if self.sd_radio.isChecked():
                text2image = "sd"
            elif self.doubao_radio.isChecked():
                text2image = "doubao"
                
            task = Task.create(
                type="text2image",
                status="pending",
                text2image=text2image,
                resolution="9:16" if self.resolution_916.isChecked() else "16:9"
            )

            if self.sd_radio.isChecked():
                stable_diffusion = StableDiffusion.select().where(StableDiffusion.name == self.sd_config_combo.currentText()).first()
            else:
                stable_diffusion = None

            # 创建工作项
            for _ in range(self.count_spinbox.value()):
                Work.create(
                    task=task,
                    super_prompt=prompt,
                    stable_diffusion=stable_diffusion,
                    status="pending"
                )

        self.accept() 