from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontMetrics
from shiyunzi.view.product_video_dialog import ProductVideoDialog
from shiyunzi.utils.models import Task, Work

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

class TaskStatusLabel(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei UI", 13))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_status(status)
        
    def update_status(self, status):
        if status == "pending":
            text = "等待中"
            bg_color = "#fef9c3"
            text_color = "#ca8a04"
        elif status == "running":
            text = "生成中"
            bg_color = "#dbeafe"
            text_color = "#2563eb"
        elif status == "completed":
            text = "已完成"
            bg_color = "#dcfce7"
            text_color = "#16a34a"
        else:  # failed
            text = "失败"
            bg_color = "#fee2e2"
            text_color = "#dc2626"
            
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 4px;
                padding: 4px 12px;
            }}
        """)
        self.setFixedWidth(80)

class TaskItem(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.task_id = task.id
        
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(0)
        
        # ID
        id_label = QLabel(str(task.id))
        id_label.setFont(QFont("Microsoft YaHei UI", 13))
        id_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(id_label, 1)
        
        # 产品
        product_label = QLabel(task.product)
        product_label.setFont(QFont("Microsoft YaHei UI", 13))
        product_label.setStyleSheet("color: #1e293b; border: none;")
        # 设置省略模式，防止文本过长
        metrics = QFontMetrics(product_label.font())
        elided_text = metrics.elidedText(task.product, Qt.TextElideMode.ElideRight, 200)
        product_label.setText(elided_text)
        product_label.setToolTip(task.product)
        layout.addWidget(product_label, 2)
        
        # 状态
        self.status_label = TaskStatusLabel(task.status)
        layout.addWidget(self.status_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # 操作按钮
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(16)
        
        open_btn = ActionButton("打开")
        open_btn.clicked.connect(self.open_video)
        actions_layout.addWidget(open_btn)
        
        delete_btn = ActionButton("删除", is_delete=True)
        delete_btn.clicked.connect(self.delete_task)
        actions_layout.addWidget(delete_btn)
        
        layout.addWidget(actions, 1)
        
    def delete_task(self):
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除任务 {self.task_id} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            task = Task.get_by_id(self.task_id)
            # 删除所有work
            Work.delete().where(Work.task == task).execute()
            # 删除task
            task.delete_instance()
            self.parent_view.load_tasks()
    
    def open_video(self):
        try:
            task = Task.get_by_id(self.task_id)
            
            # 如果任务未完成，提示用户
            if task.status != "completed":
                QMessageBox.information(
                    self,
                    "视频未完成",
                    f"任务 {self.task_id} 的视频尚未生成完成",
                    QMessageBox.StandardButton.Ok
                )
                return
                
            # 这里添加打开视频的逻辑
            # 假设视频保存在 output/product_videos/{task_id}/ 目录下
            import os
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QDesktopServices
            
            video_dir = f"output/product_videos/{task.id}"
            
            if not os.path.exists(video_dir):
                QMessageBox.warning(
                    self,
                    "视频不存在",
                    f"未找到任务 {task.id} 的视频文件",
                    QMessageBox.StandardButton.Ok
                )
                return
                
            # 打开文件夹
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(video_dir)))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"打开视频失败: {str(e)}",
                QMessageBox.StandardButton.Ok
            )

class ProductVideoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_tasks()  # 加载任务列表
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面标题和添加按钮
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        page_title = QLabel("带货视频")
        page_title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        page_title.setStyleSheet("color: #1e293b;")
        header_layout.addWidget(page_title)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(12)

        add_btn = QPushButton("+ 添加任务")
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
        add_btn.clicked.connect(self.add_task)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFont(QFont("Microsoft YaHei UI", 13))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.load_tasks)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(add_btn)
        header_layout.addWidget(buttons_container, alignment=Qt.AlignmentFlag.AlignRight)
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
        
        headers = ["ID", "产品", "状态", "操作"]
        widths = [1, 2, 1, 1]
        alignments = [Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignLeft, 
                     Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter]
        
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
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        content_layout.addWidget(self.scroll_content)
        scroll.setWidget(content_container)
        table_layout.addWidget(scroll)
        
        layout.addWidget(self.table_container)
        
    def load_tasks(self):
        # 清除现有内容
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        tasks = Task.select().where(Task.type == "product_video")
                
        for i, task in enumerate(tasks):
            if i > 0:  # 在每个项目之前添加分割线（除了第一个）
                separator = QWidget()
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: #e2e8f0;")
                self.scroll_layout.addWidget(separator)
            item = TaskItem(task, self)
            self.scroll_layout.addWidget(item)
            
        # 自动滚动到底部
        QTimer.singleShot(100, lambda: self.table_container.findChild(QScrollArea).verticalScrollBar().setValue(
            self.table_container.findChild(QScrollArea).verticalScrollBar().maximum()
        ))
            
    def add_task(self):
        dialog = ProductVideoDialog(self)
        if dialog.exec():
            self.load_tasks() 