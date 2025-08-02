import os
import subprocess
import tempfile
import ffmpeg_binaries as ffmpeg
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

# Initialize ffmpeg_binaries module
ffmpeg.init()

def run_ffmpeg_command(args_list):
    """
    运行ffmpeg命令，处理参数列表和编码问题
    """
    # 获取ffmpeg路径
    ffmpeg_path = ffmpeg.FFMPEG_PATH if hasattr(ffmpeg, 'FFMPEG_PATH') else 'ffmpeg'
    
    # 构建完整的命令
    cmd = [ffmpeg_path] + args_list
    
    try:
        # 在Windows上使用utf-8编码，并处理编码错误
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='ignore',  # 忽略编码错误
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试使用字节模式
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
            stdout = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
            stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
            return result.returncode, stdout, stderr
        except Exception as e:
            logger.error(f"执行ffmpeg命令失败: {str(e)}")
            return -1, "", str(e)
    except Exception as e:
        logger.error(f"执行ffmpeg命令失败: {str(e)}")
        return -1, "", str(e)

def apply_sticker_to_video(video_path: str, sticker_id: int, output_dir: str = None) -> str:
    """
    给视频添加贴纸
    
    Args:
        video_path: 视频文件路径
        sticker_id: 贴纸编号
        output_dir: 输出目录，如果为None则保存到原视频的同一目录
        
    Returns:
        str: 处理后的视频路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return None
        
        # 获取贴纸路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        stickers_dir = os.path.join(base_dir, "shiyunzi", "stickers")
        
        # 获取所有贴纸文件
        sticker_files = []
        
        # 直接在stickers目录下查找贴纸
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
            sticker_files.extend([f for f in Path(stickers_dir).glob(ext)])
        
        # 在子目录中查找贴纸
        for category in os.listdir(stickers_dir):
            category_path = os.path.join(stickers_dir, category)
            if os.path.isdir(category_path):
                for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                    sticker_files.extend([f for f in Path(category_path).glob(ext)])
        
        # 确保贴纸ID有效
        if not sticker_files:
            logger.error("没有找到任何贴纸")
            return None
        
        if sticker_id < 0 or sticker_id >= len(sticker_files):
            logger.error(f"贴纸ID {sticker_id} 无效，有效范围: 0-{len(sticker_files)-1}")
            return None
        
        # 获取选中的贴纸路径
        sticker_path = str(sticker_files[sticker_id])
        
        # 贴纸配置：根据文件名确定配置
        sticker_name = Path(sticker_path).stem.lower()
        
        # 特殊处理1号贴纸
        if sticker_id == 0:
            # 1号贴纸特别大
            scale_factor = "iw*0.8:-1"  # 增大到1.5倍
            x_position = "(W-w)/2"
            y_position = "(H*0.7)"
            logger.info(f"应用1号贴纸的特殊大小设置")
        # 根据贴纸名称或类型设置不同的配置
        elif "corner" in sticker_name or "角落" in sticker_name:
            # 角落贴纸 - 右下角
            scale_factor = "iw*0.45:-1"  # 增大到0.45倍
            x_position = "(W-w-20)"
            y_position = "(H-h-20)"
        elif "watermark" in sticker_name or "水印" in sticker_name:
            # 水印 - 左下角小图
            scale_factor = "iw*0.3:-1"  # 增大到0.3倍
            x_position = "20"
            y_position = "(H-h-20)"
        elif "logo" in sticker_name:
            # Logo - 右上角
            scale_factor = "iw*0.25:-1"  # 增大到0.25倍
            x_position = "(W-w-20)"
            y_position = "20"
        elif "frame" in sticker_name or "边框" in sticker_name:
            # 边框 - 覆盖整个视频
            scale_factor = "iw:ih"
            x_position = "0"
            y_position = "0"
        else:
            # 默认配置 - 居中偏下，较大尺寸
            scale_factor = "iw*0.6:-1"  # 增大到0.6倍
            x_position = "(W-w)/2"
            y_position = "(H*0.7)"
        
        # 创建输出文件路径
        video_name = os.path.basename(video_path)
        video_name_without_ext = os.path.splitext(video_name)[0]
        
        if output_dir:
            # 确保输出目录存在
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f"{video_name_without_ext}_sticker.mp4")
        else:
            # 保存到原视频的同一目录
            video_dir = os.path.dirname(video_path)
            output_path = os.path.join(video_dir, f"{video_name_without_ext}_with_sticker.mp4")
        
        logger.info(f"视频将保存到: {output_path}")
        logger.info(f"贴纸ID: {sticker_id}, 贴纸类型: {sticker_name}, 缩放比例: {scale_factor}")
        
        # 构建ffmpeg命令参数
        args = [
            "-i", video_path,
            "-i", sticker_path,
            "-filter_complex", f'[1:v]scale={scale_factor}[sticker];[0:v][sticker]overlay={x_position}:{y_position}',
            "-c:a", "copy",
            "-loglevel", "error",
            "-y", output_path
        ]
        
        logger.debug(f"执行命令: ffmpeg {' '.join(args)}")
        
        # 执行命令
        returncode, stdout, stderr = run_ffmpeg_command(args)
        
        if returncode != 0:
            logger.error(f"FFmpeg执行失败，返回码: {returncode}")
            if stderr:
                logger.error(f"错误信息: {stderr}")
            return None
        
        # 检查输出文件是否生成
        if os.path.exists(output_path):
            logger.info(f"贴纸添加完成，已保存至: {output_path}")
            return output_path
        else:
            logger.error("处理失败，输出文件不存在")
            return None
            
    except Exception as e:
        import traceback
        logger.error(f"处理视频时发生错误: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        return None

def get_sticker_preview(sticker_path: str, width: int = 120, height: int = 120) -> str:
    """
    生成贴纸预览图（如果需要处理贴纸预览）
    
    Args:
        sticker_path: 贴纸文件路径
        width: 预览宽度
        height: 预览高度
        
    Returns:
        str: 处理后的预览图路径
    """
    # 这里可以添加预览图处理逻辑，如果需要
    return sticker_path

if __name__ == "__main__":
    # 测试代码
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    stickers_dir = os.path.join(base_dir, "shiyunzi", "stickers")
    logger.info(f"贴纸目录: {stickers_dir}")
    
    # 列出所有贴纸
    sticker_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        sticker_files.extend([f for f in Path(stickers_dir).glob(ext)])
    
    for i, sticker in enumerate(sticker_files):
        logger.info(f"贴纸 {i}: {sticker.name}")
        
    # 测试添加贴纸
    video_path = "/path/to/test/video.mp4"
    if os.path.exists(video_path):
        output_path = apply_sticker_to_video(video_path, 0)
        logger.info(f"处理后的视频: {output_path}")
    else:
        logger.info("请提供有效的测试视频路径")