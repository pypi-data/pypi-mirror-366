from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontMetrics
from shiyunzi.view.text2video_dialog import Text2VideoDialog
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
        
        # 类型
        type_label = QLabel(task.type)
        type_label.setFont(QFont("Microsoft YaHei UI", 13))
        type_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(type_label, 2)

        # 文生图
        text2image_label = QLabel(task.text2image)
        text2image_label.setFont(QFont("Microsoft YaHei UI", 13))
        text2image_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(text2image_label, 1)

        # 图生视频
        image2video_label = QLabel(task.image2video)
        image2video_label.setFont(QFont("Microsoft YaHei UI", 13))
        image2video_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(image2video_label, 1)
        
        # 进度
        completed_count = Work.select().where(Work.task == task, Work.status == "completed").count()
        total_count = Work.select().where(Work.task == task).count()
        progress_label = QLabel(f"{completed_count}/{total_count}")
        progress_label.setFont(QFont("Microsoft YaHei UI", 13))
        progress_label.setStyleSheet("color: #1e293b; border: none;")
        progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(progress_label, 1)
        
        # 状态
        self.status_label = TaskStatusLabel(task.status)
        layout.addWidget(self.status_label, 1, Qt.AlignmentFlag.AlignCenter)
        
        # 操作按钮
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(16)
        
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

class Text2VideoView(QWidget):
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
        
        page_title = QLabel("文生视频")
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
        
        headers = ["ID", "类型", "文生图", "图生视频", "进度", "状态", "操作"]
        widths = [1, 2, 1, 1, 1, 1, 1]
        alignments = [Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignLeft, 
                     Qt.AlignmentFlag.AlignLeft, Qt.AlignmentFlag.AlignLeft,
                     Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter,
                     Qt.AlignmentFlag.AlignCenter]
        
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

        tasks = Task.select().where(Task.type == "text2video")
                
        for i, task in enumerate(tasks):
            # 检查任务状态
            completed_count = Work.select().where(Work.task == task, Work.status == "completed").count()
            total_count = Work.select().where(Work.task == task).count()
            
            # 如果total_count为0，跳过这个任务
            if total_count == 0:
                continue
                
            # 只有当所有work都完成时才更新task状态为completed
            if completed_count == total_count:
                if task.status != "completed":
                    task.status = "completed"
                    task.save()
            else:
                # 如果有未完成的work，确保task状态不是completed
                if task.status == "completed":
                    task.status = "running"
                    task.save()
            
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
        dialog = Text2VideoDialog(self)
        if dialog.exec():
            prompt = dialog.prompt
            self.load_tasks() 
