from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFrame, QDialog,
                           QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap
from shiyunzi.utils.models import StableDiffusion
from shiyunzi.view.sd_edit_dialog import SDEditDialog
from shiyunzi.llm.genmini_util import google_video2text
import os

class VideoUploadDialog(QDialog):
    def __init__(self, analysis_type="single", parent=None):
        super().__init__(parent)
        self.analysis_type = analysis_type
        self.video_path = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("视频解析")
        self.setFixedSize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题
        title_container = QWidget()
        title_container.setStyleSheet("background-color: #ffffff;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(32, 32, 32, 32)
        
        title = QLabel("视频解析" if self.analysis_type == "single" else "上传多个视频")
        title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; border: none;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("支持 MP4、AVI、MOV、MKV 格式")
        subtitle.setFont(QFont("Microsoft YaHei UI", 13))
        subtitle.setStyleSheet("color: #64748b; border: none;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        
        # 拖放区域
        drop_area = DropArea(self)
        drop_area.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 2px dashed #e2e8f0;
                border-radius: 12px;
                margin: 0 32px 32px 32px;
            }
            QFrame:hover {
                border-color: #6366f1;
                background-color: #f1f5f9;
            }
        """)
        
        drop_layout = QVBoxLayout(drop_area)
        drop_layout.setContentsMargins(0, 40, 0, 40)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 上传图标
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #e2e8f0;
                border-radius: 32px;
            }
        """)
        drop_layout.addWidget(icon_label)
        
        # 提示文本
        hint_label = QLabel("点击或拖拽视频到这里上传")
        hint_label.setFont(QFont("Microsoft YaHei UI", 16))
        hint_label.setStyleSheet("color: #1e293b; border: none;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(hint_label)
        
        format_label = QLabel("仅支持 MP4、AVI、MOV、MKV 格式")
        format_label.setFont(QFont("Microsoft YaHei UI", 13))
        format_label.setStyleSheet("color: #64748b; border: none;")
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(format_label)
        
        layout.addWidget(drop_area)
        
    def mousePressEvent(self, event):
        self.select_video()
        
    def select_video(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("视频文件 (*.mp4 *.avi *.mov *.mkv)")
        file_dialog.setWindowTitle("选择视频文件")
        if self.analysis_type == "multi":
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        
        if file_dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = file_dialog.selectedFiles()
            self.video_path = filenames[0] if self.analysis_type == "single" else filenames
            self.accept()

class DropArea(QFrame):
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if self.dialog.analysis_type == "single" and len(urls) > 1:
                event.ignore()
                return
                
            for url in urls:
                if not url.isLocalFile():
                    event.ignore()
                    return
                    
                file_path = url.toLocalFile()
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in ['.mp4', '.avi', '.mov', '.mkv']:
                    event.ignore()
                    return
                    
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            paths = [url.toLocalFile() for url in urls]
            self.dialog.video_path = paths[0] if self.dialog.analysis_type == "single" else paths
            self.dialog.accept()
            
    def mousePressEvent(self, event):
        self.dialog.select_video()

class AnalysisCard(QFrame):
    def __init__(self, title, description, analysis_type="single", enabled=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.analysis_type = analysis_type
        self.enabled = enabled
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(360, 120)
        if self.enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 根据启用状态设置样式
        base_style = """
            QFrame {
                background-color: #ffffff;
                border: 1px solid %s;
                border-radius: 12px;
            }
        """ % ("#e2e8f0" if self.enabled else "#f1f5f9")
        
        hover_style = """
            QFrame:hover {
                border-color: #6366f1;
            }
        """ if self.enabled else ""
        
        self.setStyleSheet(base_style + hover_style)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {('#1e293b' if self.enabled else '#94a3b8')}; border: none;")
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("Microsoft YaHei UI", 13))
        desc_label.setStyleSheet(f"color: {('#64748b' if self.enabled else '#cbd5e1')}; border: none;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
    def mousePressEvent(self, event):
        if not self.enabled:
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = VideoUploadDialog(self.analysis_type, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.start_analysis(dialog.video_path)
                
    def start_analysis(self, video_path):
        if isinstance(video_path, str):
            # 单视频分析
            output_path = os.path.splitext(video_path)[0] + "_解析.md"
            try:
                # TODO: 这里添加实际的视频分析逻辑
                result = google_video2text(video_path=video_path)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                QMessageBox.information(self, "分析完成", f"分析结果已保存到：{output_path}")
            except Exception as e:
                QMessageBox.warning(self, "分析失败", f"分析视频时发生错误：{str(e)}")
        else:
            # 多视频分析
            for path in video_path:
                output_path = os.path.splitext(path)[0] + "_解析.md"
                try:
                    # TODO: 这里添加实际的视频分析逻辑
                    with open(output_path, 'w', encoding='utf-8') as f:
                        pass
                except Exception as e:
                    QMessageBox.warning(self, "分析失败", f"分析视频 {path} 时发生错误：{str(e)}")
            QMessageBox.information(self, "分析完成", "所有视频分析完成")

class VideoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # 标题
        title = QLabel("视频解析")
        title.setFont(QFont("Microsoft YaHei UI", 24, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 8px; border: none;")
        layout.addWidget(title)
        
        # 卡片容器
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(24)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 添加分析卡片
        single_card = AnalysisCard(
            "单镜头解析",
            "上传单个视频文件进行分析",
            "single",
            True
        )
        cards_layout.addWidget(single_card)
        
        multi_card = AnalysisCard(
            "多镜头解析",
            "同时分析多个视频文件",
            "multi",
            False  # 禁用多镜头解析
        )
        cards_layout.addWidget(multi_card)
        
        layout.addWidget(cards_container)
        layout.addStretch() 