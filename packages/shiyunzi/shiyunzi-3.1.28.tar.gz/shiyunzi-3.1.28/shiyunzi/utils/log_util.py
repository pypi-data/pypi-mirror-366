import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import shutil
import time
import subprocess
import zipfile
# 定义常量
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 9  # 保留9个备份文件，加上当前文件共10个

# 全局变量，用于存储当前会话的日志文件路径
_current_log_file = None

def get_logger(name=None):
    """
    获取logger实例
    :param name: logger名称，通常使用模块名 __name__
    :return: logger实例
    """
    global _current_log_file
    
    # 如果没有指定名称，使用root logger
    logger = logging.getLogger(name or "shiyunzi")
    
    # 如果logger已经配置过，直接返回
    if logger.handlers:
        return logger
        
    # 设置日志级别
    logger.setLevel(logging.INFO)
    # 阻止日志传递到父logger
    logger.propagate = False
    
    # 获取日志目录
    if sys.platform == "darwin":  # macOS
        base_path = os.path.expanduser("~/Library/Logs")
    elif sys.platform == "win32":  # Windows
        base_path = os.path.expandvars("%LOCALAPPDATA%")
    else:  # Fallback for other platforms
        base_path = os.path.expanduser("~/.logs")
    
    log_dir = os.path.join(base_path, "shiyunzi")
    os.makedirs(log_dir, exist_ok=True)
    
    # 如果是首次创建日志文件，使用当前日期时间创建文件名
    if _current_log_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # 使用更易读的日期格式
        _current_log_file = os.path.join(log_dir, f"shiyunzi_{timestamp}.log")
    
    # 检查是否已经存在相同的handler
    has_file_handler = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    has_console_handler = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in logger.handlers)
    
    # 创建格式化器
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'  # 自定义时间格式
    )
    
    # 只在没有对应handler时添加新的handler
    if not has_file_handler:
        # 使用FileHandler，确保所有日志写入同一个文件
        file_handler = logging.FileHandler(
            _current_log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    if not has_console_handler:
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

# Create a default logger instance
default_logger = get_logger()

# Convenience functions
def debug(message):
    default_logger.debug(message)

def info(message):
    default_logger.info(message)

def warning(message):
    default_logger.warning(message)

def error(message):
    default_logger.error(message)

def critical(message):
    default_logger.critical(message) 

def get_log_file_path():
    if sys.platform == "darwin":  # macOS
        base_path = os.path.expanduser("~/Library/Logs")
    elif sys.platform == "win32":  # Windows
        base_path = os.path.expandvars("%LOCALAPPDATA%")
    else:  # Fallback for other platforms
        base_path = os.path.expanduser("~/.logs")
    
    log_dir = os.path.join(base_path, "shiyunzi")
    return log_dir

#打包日志文件
def pack_log_file():
    log_dir = get_log_file_path()
    # 获取桌面路径
    desktop = os.path.expanduser("~/Desktop")
    # 生成zip文件名,使用当前时间戳
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_name = f"shiyunzi_logs_{timestamp}.zip"
    zip_path = os.path.join(desktop, zip_name)
    
    # 创建zip文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历日志目录
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 将文件添加到zip中,使用相对路径
                arcname = os.path.relpath(file_path, os.path.dirname(log_dir))
                zipf.write(file_path, arcname)