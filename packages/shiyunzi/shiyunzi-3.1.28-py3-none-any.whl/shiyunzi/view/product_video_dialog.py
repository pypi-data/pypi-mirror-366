from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QFileDialog,
                           QComboBox, QMessageBox, QSpinBox, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shiyunzi.utils.models import Task, Work
import uuid
import os

class ProductVideoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加带货视频任务")
        self.resize(600, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("添加带货视频任务")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 12px;")
        layout.addWidget(title)
        
        # 1. 人像文件夹
        portrait_layout = QHBoxLayout()
        portrait_label = QLabel("人像文件夹:")
        portrait_label.setFont(QFont("Microsoft YaHei UI", 13))
        portrait_label.setStyleSheet("color: #1e293b;")
        portrait_layout.addWidget(portrait_label)
        
        self.portrait_input = QLineEdit()
        self.portrait_input.setFont(QFont("Microsoft YaHei UI", 13))
        self.portrait_input.setReadOnly(True)
        self.portrait_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #f8fafc;
            }
        """)
        portrait_layout.addWidget(self.portrait_input)
        
        portrait_browse_btn = QPushButton("浏览")
        portrait_browse_btn.setFont(QFont("Microsoft YaHei UI", 13))
        portrait_browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        portrait_browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        portrait_browse_btn.clicked.connect(self.browse_portrait)
        portrait_layout.addWidget(portrait_browse_btn)
        layout.addLayout(portrait_layout)
        
        # 产品名称
        product_layout = QHBoxLayout()
        product_label = QLabel("产品名称:")
        product_label.setFont(QFont("Microsoft YaHei UI", 13))
        product_label.setStyleSheet("color: #1e293b;")
        product_layout.addWidget(product_label)
        
        self.product_input = QLineEdit()
        self.product_input.setFont(QFont("Microsoft YaHei UI", 13))
        self.product_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        product_layout.addWidget(self.product_input)
        layout.addLayout(product_layout)
        
        # 2. 产品图片
        image_layout = QHBoxLayout()
        image_label = QLabel("产品图片:")
        image_label.setFont(QFont("Microsoft YaHei UI", 13))
        image_label.setStyleSheet("color: #1e293b;")
        image_layout.addWidget(image_label)
        
        self.image_input = QLineEdit()
        self.image_input.setFont(QFont("Microsoft YaHei UI", 13))
        self.image_input.setReadOnly(True)
        self.image_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #f8fafc;
            }
        """)
        image_layout.addWidget(self.image_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.setFont(QFont("Microsoft YaHei UI", 13))
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_btn)
        layout.addLayout(image_layout)
        
        # 3. 产品描述
        desc_label = QLabel("产品描述:")
        desc_label.setFont(QFont("Microsoft YaHei UI", 13))
        desc_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setFont(QFont("Microsoft YaHei UI", 13))
        self.desc_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QTextEdit:focus {
                border-color: #6366f1;
            }
        """)
        self.desc_input.setFixedHeight(80)
        layout.addWidget(self.desc_input)
        
        # 4. 钩子
        hook_label = QLabel("钩子:")
        hook_label.setFont(QFont("Microsoft YaHei UI", 13))
        hook_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(hook_label)
        
        self.hook_input = QTextEdit()
        self.hook_input.setFont(QFont("Microsoft YaHei UI", 13))
        self.hook_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QTextEdit:focus {
                border-color: #6366f1;
            }
        """)
        self.hook_input.setFixedHeight(80)
        layout.addWidget(self.hook_input)
        
        # 5. 生成个数
        count_layout = QHBoxLayout()
        count_label = QLabel("生成个数:")
        count_label.setFont(QFont("Microsoft YaHei UI", 13))
        count_label.setStyleSheet("color: #1e293b;")
        count_layout.addWidget(count_label)
        
        self.count_spin = QSpinBox()
        self.count_spin.setFont(QFont("Microsoft YaHei UI", 13))
        self.count_spin.setRange(1, 10)
        self.count_spin.setValue(1)
        self.count_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QSpinBox:focus {
                border-color: #6366f1;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
            }
        """)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        layout.addLayout(count_layout)
        
        # 视频类型
        type_layout = QHBoxLayout()
        type_label = QLabel("视频类型:")
        type_label.setFont(QFont("Microsoft YaHei UI", 13))
        type_label.setStyleSheet("color: #1e293b;")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.setFont(QFont("Microsoft YaHei UI", 13))
        self.type_combo.addItems(["短视频", "直播", "长视频"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QComboBox:focus {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
        """)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFont(QFont("Microsoft YaHei UI", 13))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #475569;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("创建")
        create_btn.setFont(QFont("Microsoft YaHei UI", 13))
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        create_btn.clicked.connect(self.create_task)
        buttons_layout.addWidget(create_btn)
        
        layout.addLayout(buttons_layout)
        
    def browse_portrait(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择人像文件夹", ""
        )
        if folder_path:
            self.portrait_input.setText(folder_path)
        
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择产品图片", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.image_input.setText(file_path)
            
    def create_task(self):
        portrait_path = self.portrait_input.text()
        product = self.product_input.text().strip()
        image_path = self.image_input.text()
        description = self.desc_input.toPlainText().strip()
        hook = self.hook_input.toPlainText().strip()
        count = self.count_spin.value()
        video_type = self.type_combo.currentText()
        
        if not portrait_path:
            QMessageBox.warning(self, "警告", "请选择人像文件夹")
            return
            
        if not os.path.isdir(portrait_path):
            QMessageBox.warning(self, "警告", "人像文件夹不存在")
            return
            
        if not product:
            QMessageBox.warning(self, "警告", "请输入产品名称")
            return
            
        if not image_path:
            QMessageBox.warning(self, "警告", "请选择产品图片")
            return
            
        if not description:
            QMessageBox.warning(self, "警告", "请输入产品描述")
            return
            
        if not hook:
            QMessageBox.warning(self, "警告", "请输入钩子")
            return
            
        try:
            # 创建任务
            task = Task.create(
                id=str(uuid.uuid4()),
                type="product_video",
                status="pending",
                product=product,
                video_type=video_type,
                image_path=image_path,
                portrait_path=portrait_path,
                description=description,
                hook=hook
            )
            
            # 创建工作项
            for i in range(count):
                Work.create(
                    id=str(uuid.uuid4()),
                    task=task,
                    status="pending"
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建任务失败: {str(e)}")
            self.reject() 