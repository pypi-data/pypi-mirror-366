from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QFrame,
                           QMenu, QMessageBox, QDialog, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from shiyunzi.utils.models import StableDiffusion
from shiyunzi.view.sd_edit_dialog import SDEditDialog
import os
import json
from pathlib import Path

class SDCard(QFrame):
    def __init__(self, sd_data: StableDiffusion, parent=None):
        super().__init__(parent)
        self.sd_data = sd_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(360, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
        
        # 标题行
        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet("border: none;")
        
        # 加载 SVG 图标
        svg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "stable_diffusion.svg")
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon_label.setPixmap(pixmap)
        title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(self.sd_data.name)
        title_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #1e293b; border: none;")
        title_layout.addWidget(title_label)
        
        # 模型名称标签
        model_label = QLabel(self.sd_data.model)
        model_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 12px;
                border: none;
            }
        """)
        title_layout.addWidget(model_label)
        title_layout.addStretch()
        
        layout.addWidget(title_row)
        
        # 描述文本
        desc_label = QLabel(f"Steps: {self.sd_data.steps} | CFG: {self.sd_data.cfg} | {self.sd_data.width}x{self.sd_data.height}")
        desc_label.setFont(QFont("Microsoft YaHei UI", 12))
        desc_label.setStyleSheet("color: #64748b; border: none;")
        layout.addWidget(desc_label)
        
    def export_config(self):
        # 获取桌面路径
        desktop = str(Path.home() / "Desktop")
        filename = os.path.join(desktop, f"{self.sd_data.name}.json")
        
        # 准备导出数据
        export_data = {
            'name': self.sd_data.name,
            'model': self.sd_data.model,
            'lora': self.sd_data.lora,
            'prompt': self.sd_data.prompt,
            'negative_prompt': self.sd_data.negative_prompt,
            'steps': self.sd_data.steps,
            'cfg': self.sd_data.cfg,
            'scheduler': self.sd_data.scheduler,
            'sampler': self.sd_data.sampler,
            'seed': self.sd_data.seed,
            'width': self.sd_data.width,
            'height': self.sd_data.height
        }
        
        # 写入文件
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "导出成功", f"配置已导出到：{filename}")
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出配置时发生错误：{str(e)}")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = SDEditDialog(self.sd_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if isinstance(self.parent(), QWidget):
                    parent = self.parent()
                    while parent and not isinstance(parent, SDView):
                        parent = parent.parent()
                    if parent:
                        parent.load_configs()
        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 24px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #f1f5f9;
                }
            """)
            
            export_action = menu.addAction("导出配置")
            delete_action = menu.addAction("删除")
            
            action = menu.exec(QCursor.pos())
            
            if action == export_action:
                self.export_config()
            elif action == delete_action:
                reply = QMessageBox.question(
                    self,
                    "确认删除",
                    f"确定要删除配置 '{self.sd_data.name}' 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.sd_data.delete_instance()
                    if isinstance(self.parent(), QWidget):
                        parent = self.parent()
                        while parent and not isinstance(parent, SDView):
                            parent = parent.parent()
                        if parent:
                            parent.load_configs()

class SDView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # 标题和按钮行
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # 标题
        title = QLabel("Stable Diffusion")
        title.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 8px; border: none;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 导入按钮
        import_btn = QPushButton("导入配置")
        import_btn.setFont(QFont("Microsoft YaHei UI", 13))
        import_btn.setMinimumSize(100, 36)
        import_btn.setStyleSheet("""
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
        import_btn.clicked.connect(self.import_config)
        header_layout.addWidget(import_btn)
        
        # 添加按钮
        add_btn = QPushButton("添加配置")
        add_btn.setFont(QFont("Microsoft YaHei UI", 13))
        add_btn.setMinimumSize(100, 36)
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_config)
        header_layout.addWidget(add_btn)
        
        layout.addWidget(header)
        
        # 卡片容器
        cards_container = QWidget()
        self.cards_layout = QVBoxLayout(cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(24)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 加载现有配置
        self.load_configs()
        
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
        
    def import_config(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("JSON 文件 (*.json)")
        file_dialog.setWindowTitle("选择配置文件")
        
        if file_dialog.exec() == QDialog.DialogCode.Accepted:
            filename = file_dialog.selectedFiles()[0]
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 创建新配置
                StableDiffusion.create(
                    name=data.get('name', ''),
                    model=data.get('model', ''),
                    lora=data.get('lora', ''),
                    prompt=data.get('prompt', ''),
                    negative_prompt=data.get('negative_prompt', ''),
                    steps=data.get('steps', 20),
                    cfg=data.get('cfg', 7),
                    scheduler=data.get('scheduler', ''),
                    sampler=data.get('sampler', ''),
                    seed=data.get('seed', -1),
                    width=data.get('width', 512),
                    height=data.get('height', 512)
                )
                
                self.load_configs()
                QMessageBox.information(self, "导入成功", "配置已成功导入")
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"导入配置时发生错误：{str(e)}")
        
    def load_configs(self):
        # 清除现有卡片
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 加载配置，按创建时间倒序排列
        configs = StableDiffusion.select().order_by(StableDiffusion.created_at.desc())
        
        # 创建行容器
        current_row = None
        for i, config in enumerate(configs):
            if i % 2 == 0:
                current_row = QWidget()
                row_layout = QHBoxLayout(current_row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(24)
                row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.cards_layout.addWidget(current_row)
            
            card = SDCard(config)
            row_layout.addWidget(card)
            
            # 不再添加 stretch，这样卡片会靠左对齐
        
    def add_config(self):
        dialog = SDEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_configs() 