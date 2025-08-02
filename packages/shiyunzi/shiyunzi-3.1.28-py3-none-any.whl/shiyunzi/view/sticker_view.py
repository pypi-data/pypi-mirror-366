from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QPushButton, QLabel, QScrollArea, QMessageBox, QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage
from shiyunzi.utils.sticker_util import apply_sticker_to_video
import os
import glob
from pathlib import Path

class StickerThread(QThread):
    """处理贴纸应用的线程"""
    progress_signal = pyqtSignal(int, int)  # 当前进度, 总数
    finished_signal = pyqtSignal(bool, str)  # 成功/失败, 消息

    def __init__(self, video_dir, sticker_id):
        super().__init__()
        self.video_dir = video_dir
        self.sticker_id = sticker_id
        
    def run(self):
        try:
            # 获取目录中的所有视频文件
            video_files = []
            for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
                video_files.extend(glob.glob(os.path.join(self.video_dir, ext)))
            
            total = len(video_files)
            if total == 0:
                self.finished_signal.emit(False, "所选文件夹中没有找到视频文件")
                return
            
            # 创建输出目录
            output_dir = os.path.join(self.video_dir, "贴纸处理结果")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # 处理每个视频文件
            for i, video_file in enumerate(video_files):
                try:
                    # 更新进度
                    self.progress_signal.emit(i + 1, total)
                    
                    # 应用贴纸
                    output_path = apply_sticker_to_video(video_file, self.sticker_id, output_dir)
                    
                except Exception as e:
                    print(f"处理视频 {video_file} 时出错: {str(e)}")
                    # 继续处理下一个视频
            
            self.finished_signal.emit(True, f"成功处理 {total} 个视频文件，已保存到 {output_dir}")
            
        except Exception as e:
            self.finished_signal.emit(False, f"处理失败: {str(e)}")


class StickerItem(QWidget):
    """贴纸项目组件"""
    def __init__(self, sticker_id, sticker_path, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.sticker_id = sticker_id
        self.sticker_path = sticker_path
        
        self.setFixedSize(150, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QWidget:hover {
                border-color: #6366f1;
                background-color: #eff6ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 贴纸图片
        image_container = QWidget()
        image_container.setFixedSize(130, 130)
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: none; background: transparent;")
        
        # 加载图片
        pixmap = QPixmap(sticker_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("图片加载失败")
            
        image_layout.addWidget(self.image_label)
        layout.addWidget(image_container)
        
        # 贴纸名称
        name_label = QLabel(Path(sticker_path).stem)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("Microsoft YaHei UI", 12))
        name_label.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        layout.addWidget(name_label)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_view.select_sticker(self.sticker_id)
        super().mousePressEvent(event)


class StickerView(QWidget):
    """贴纸功能主视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sticker_thread = None
        self.setup_ui()
        self.load_stickers()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面标题
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        page_title = QLabel("贴纸功能")
        page_title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        page_title.setStyleSheet("color: #1e293b;")
        header_layout.addWidget(page_title)
        
        header_layout.addStretch()
        layout.addWidget(header)
        
        # 说明文本
        instruction = QLabel("点击贴纸可将其应用到选定文件夹中的所有视频")
        instruction.setFont(QFont("Microsoft YaHei UI", 13))
        instruction.setStyleSheet("color: #64748b; margin-bottom: 16px;")
        layout.addWidget(instruction)
        
        # 贴纸展示区域
        sticker_container = QWidget()
        sticker_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
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
        
        self.sticker_grid = QWidget()
        self.grid_layout = QGridLayout(self.sticker_grid)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.sticker_grid)
        
        sticker_layout = QVBoxLayout(sticker_container)
        sticker_layout.setContentsMargins(0, 0, 0, 0)
        sticker_layout.addWidget(scroll)
        
        layout.addWidget(sticker_container)
        
        # 进度显示区域
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m - %p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                background-color: #f8fafc;
                text-align: center;
                height: 24px;
                font-size: 13px;
                font-family: "Microsoft YaHei UI";
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 3px;
            }
        """)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Microsoft YaHei UI", 13))
        self.status_label.setStyleSheet("color: #6366f1;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        # 默认隐藏进度区域
        progress_container.setVisible(False)
        self.progress_container = progress_container
        
        layout.addWidget(progress_container)
        
    def load_stickers(self):
        """加载所有贴纸"""
        # 清除现有内容
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取贴纸路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        stickers_dir = os.path.join(base_dir, "shiyunzi", "stickers")
        
        # 确保目录存在
        if not os.path.exists(stickers_dir):
            os.makedirs(stickers_dir)
        
        # 加载所有贴纸
        sticker_files = []
        
        # 直接在stickers目录下查找贴纸
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
            sticker_files.extend(glob.glob(os.path.join(stickers_dir, ext)))
        
        # 在子目录中查找贴纸
        for category in os.listdir(stickers_dir):
            category_path = os.path.join(stickers_dir, category)
            if os.path.isdir(category_path):
                for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                    sticker_files.extend(glob.glob(os.path.join(category_path, ext)))
        
        # 添加贴纸到网格
        if not sticker_files:
            empty_label = QLabel("没有找到贴纸，请将贴纸图片放入 shiyunzi/stickers 目录")
            empty_label.setFont(QFont("Microsoft YaHei UI", 14))
            empty_label.setStyleSheet("color: #64748b;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            return
            
        # 添加贴纸到网格
        row, col = 0, 0
        max_cols = 4  # 每行最多显示的贴纸数
        
        for i, sticker_path in enumerate(sticker_files):
            sticker_item = StickerItem(i, sticker_path, self)
            self.grid_layout.addWidget(sticker_item, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def select_sticker(self, sticker_id):
        """选择贴纸并弹出文件夹选择对话框"""
        # 选择文件夹
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "选择视频文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            return
            
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认应用贴纸",
            f"确定要将选中的贴纸应用到文件夹 {folder_path} 中的所有视频吗？\n"
            f"处理后的视频将保存到 '{folder_path}/贴纸处理结果' 文件夹",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # 启动处理线程
        if self.sticker_thread is not None and self.sticker_thread.isRunning():
            QMessageBox.warning(self, "警告", "有正在进行的任务，请等待完成")
            return
        
        # 显示进度区域
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在处理视频...")
        
        self.sticker_thread = StickerThread(folder_path, sticker_id)
        self.sticker_thread.progress_signal.connect(self.update_progress)
        self.sticker_thread.finished_signal.connect(self.process_finished)
        self.sticker_thread.start()
    
    def update_progress(self, current, total):
        """更新进度显示"""
        progress_percent = int(current * 100 / total)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"正在处理: {current}/{total} 个视频")
    
    def process_finished(self, success, message):
        """处理完成回调"""
        if success:
            self.status_label.setText("处理完成")
            QMessageBox.information(self, "处理完成", message)
        else:
            self.status_label.setText("处理失败")
            QMessageBox.warning(self, "处理失败", message) 