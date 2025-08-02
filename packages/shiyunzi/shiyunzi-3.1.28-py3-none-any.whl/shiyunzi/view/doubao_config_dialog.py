from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFormLayout, QWidget
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import sys
import os
from shiyunzi.utils.config_util import set_config, get_config
from shiyunzi.utils.log_util import get_logger
from shiyunzi.doubao.cookie_fetcher import DoubaoCookieFetcher

logger = get_logger(__name__)

class FetchThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def run(self):
        try:
            logger.info("开始抓取豆包配置线程")
            fetcher = DoubaoCookieFetcher(status_callback=self.update_status)
            result = fetcher.fetch()
            self.finished_signal.emit(result)
        except Exception as e:
            logger.error(f"抓取豆包配置失败: {str(e)}")
            self.error_signal.emit(f"抓取失败: {str(e)}")
    
    def update_status(self, status):
        # 只记录日志，不显示到界面
        logger.info(f"抓取状态: {status}")

class DoubaoConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("豆包配置")
        self.setFixedSize(500, 600)  # 大幅增加对话框高度
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        self.setup_ui()
        self.load_config()
        self.fetch_thread = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(35)  # 增加主布局的间距
        
        # 标题
        title = QLabel("豆包配置")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; border: none; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 表单
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 10)  # 增加上下内边距
        form_layout.setSpacing(30)  # 增加表单项之间的间距
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setVerticalSpacing(35)  # 进一步增加垂直间距
        form_layout.setHorizontalSpacing(20)  # 增加水平间距
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)  # 确保行不会被换行
        
        # 确保表单容器有足够的空间
        form_container.setMinimumHeight(400)  # 大幅增加表单容器最小高度
        
        # 输入框样式
        input_style = """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1e293b;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """
        
        # Device ID
        self.device_id_edit = QLineEdit()
        self.device_id_edit.setMinimumWidth(300)
        self.device_id_edit.setMinimumHeight(36)
        self.device_id_edit.setFrame(False)
        self.device_id_edit.setStyleSheet(input_style)
        device_id_label = QLabel("Device ID:")
        device_id_label.setStyleSheet("border: none;")
        form_layout.addRow(device_id_label, self.device_id_edit)
        
        # Tea UUID
        self.tea_uuid_edit = QLineEdit()
        self.tea_uuid_edit.setMinimumWidth(300)
        self.tea_uuid_edit.setMinimumHeight(36)
        self.tea_uuid_edit.setFrame(False)
        self.tea_uuid_edit.setStyleSheet(input_style)
        tea_uuid_label = QLabel("Tea UUID:")
        tea_uuid_label.setStyleSheet("border: none;")
        form_layout.addRow(tea_uuid_label, self.tea_uuid_edit)
        
        # Web ID
        self.web_id_edit = QLineEdit()
        self.web_id_edit.setMinimumWidth(300)
        self.web_id_edit.setMinimumHeight(36)
        self.web_id_edit.setFrame(False)
        self.web_id_edit.setStyleSheet(input_style)
        web_id_label = QLabel("Web ID:")
        web_id_label.setStyleSheet("border: none;")
        form_layout.addRow(web_id_label, self.web_id_edit)
        
        # Cookies
        self.cookies_edit = QLineEdit()
        self.cookies_edit.setMinimumWidth(300)
        self.cookies_edit.setMinimumHeight(36)
        self.cookies_edit.setFrame(False)
        self.cookies_edit.setStyleSheet(input_style)
        cookies_label = QLabel("Cookies:")
        cookies_label.setStyleSheet("border: none;")
        form_layout.addRow(cookies_label, self.cookies_edit)
        
        # X-Flow-Trace
        self.x_flow_trace_edit = QLineEdit()
        self.x_flow_trace_edit.setMinimumWidth(300)
        self.x_flow_trace_edit.setMinimumHeight(36)
        self.x_flow_trace_edit.setFrame(False)
        self.x_flow_trace_edit.setStyleSheet(input_style)
        x_flow_trace_label = QLabel("X-Flow-Trace:")
        x_flow_trace_label.setStyleSheet("border: none;")
        form_layout.addRow(x_flow_trace_label, self.x_flow_trace_edit)
        
        # Room ID
        self.room_id_edit = QLineEdit()
        self.room_id_edit.setMinimumWidth(300)
        self.room_id_edit.setMinimumHeight(36)
        self.room_id_edit.setFrame(False)
        self.room_id_edit.setStyleSheet(input_style)
        room_id_label = QLabel("Room ID:")
        room_id_label.setStyleSheet("border: none;")
        form_layout.addRow(room_id_label, self.room_id_edit)
        
        layout.addWidget(form_container)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        # 自动抓取按钮 - 隐藏
        self.fetch_button = QPushButton("自动抓取")
        self.fetch_button.setMinimumSize(100, 36)
        self.fetch_button.setFont(QFont("Microsoft YaHei UI", 13))
        self.fetch_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.fetch_button.clicked.connect(self.start_fetch)
        self.fetch_button.setVisible(False)  # 设置为不可见
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumSize(100, 36)
        self.cancel_button.setFont(QFont("Microsoft YaHei UI", 13))
        self.cancel_button.setStyleSheet("""
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
        self.cancel_button.clicked.connect(self.reject)
        
        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setMinimumSize(100, 36)
        self.save_button.setFont(QFont("Microsoft YaHei UI", 13))
        self.save_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.save_button.clicked.connect(self.save_and_exit)
        
        button_layout.addWidget(self.fetch_button)  # 仍然添加到布局，但不可见
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addWidget(button_container)
        
    def load_config(self):
        try:
            # 分别获取各个配置项
            self.device_id_edit.setText(str(get_config("doubao_device_id") or ''))
            self.tea_uuid_edit.setText(str(get_config("doubao_tea_uuid") or ''))
            self.web_id_edit.setText(str(get_config("doubao_web_id") or ''))
            self.cookies_edit.setText(str(get_config("doubao_cookie") or ''))
            self.x_flow_trace_edit.setText(str(get_config("doubao_x_flow_trace") or ''))
            self.room_id_edit.setText(str(get_config("doubao_room_id") or ''))
            
            logger.info("成功加载豆包配置")
        except Exception as e:
            # 捕获所有异常，确保UI能正常显示
            logger.error(f"加载配置时出错: {str(e)}")
            self.device_id_edit.setText('')
            self.tea_uuid_edit.setText('')
            self.web_id_edit.setText('')
            self.cookies_edit.setText('')
            self.x_flow_trace_edit.setText('')
            self.room_id_edit.setText('')
            
    def save_and_exit(self):
        try:
            # 分别保存各个配置项
            set_config("doubao_device_id", self.device_id_edit.text())
            set_config("doubao_tea_uuid", self.tea_uuid_edit.text())
            set_config("doubao_web_id", self.web_id_edit.text())
            set_config("doubao_cookie", self.cookies_edit.text())
            set_config("doubao_x_flow_trace", self.x_flow_trace_edit.text())
            set_config("doubao_room_id", self.room_id_edit.text())
            
            logger.info("成功保存豆包配置")
            
            # 提示用户需要重启应用
            QMessageBox.information(self, "配置已保存", "配置已保存，应用将重启以应用更改。")
            
            # 关闭当前进程并重启应用
            self.restart_application()
        except Exception as e:
            logger.error(f"保存配置时出错: {str(e)}")
            QMessageBox.critical(self, "保存失败", f"保存配置失败: {str(e)}")
            
    def restart_application(self):
        """关闭当前进程并重启应用"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
        
    def start_fetch(self):
        """开始自动抓取豆包配置"""
        logger.info("开始自动抓取豆包配置")
        
        # 禁用按钮，防止重复点击
        self.fetch_button.setEnabled(False)
        self.save_button.setEnabled(False)
        
        # 创建并启动抓取线程
        self.fetch_thread = FetchThread()
        self.fetch_thread.finished_signal.connect(self.fetch_finished)
        self.fetch_thread.error_signal.connect(self.fetch_error)
        self.fetch_thread.start()
        
    def fetch_finished(self, result):
        """抓取完成后的处理"""
        try:
            # 更新表单
            self.device_id_edit.setText(str(result.get('device_id', '')))
            self.tea_uuid_edit.setText(str(result.get('tea_uuid', '')))
            self.web_id_edit.setText(str(result.get('web_id', '')))
            self.cookies_edit.setText(str(result.get('cookies', '')))
            self.x_flow_trace_edit.setText(str(result.get('x_flow_trace', '')))
            self.room_id_edit.setText(str(result.get('room_id', '')))
            
            # 恢复按钮状态
            self.fetch_button.setEnabled(True)
            self.save_button.setEnabled(True)
            
            # 显示成功消息
            QMessageBox.information(self, "抓取成功", "成功抓取豆包配置信息，请点击保存按钮保存配置。")
        except Exception as e:
            logger.error(f"更新表单时出错: {str(e)}")
            QMessageBox.critical(self, "更新失败", f"更新表单时出错: {str(e)}")
        
    def fetch_error(self, error_msg):
        """抓取出错的处理"""
        logger.error(f"抓取豆包配置失败: {error_msg}")
        
        # 显示错误消息
        QMessageBox.critical(self, "抓取失败", error_msg)
        
        # 恢复按钮状态
        self.fetch_button.setEnabled(True)
        self.save_button.setEnabled(True) 
        