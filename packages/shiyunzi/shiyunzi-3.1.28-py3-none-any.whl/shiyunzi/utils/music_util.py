import os
import shutil
import subprocess
import ffmpeg_binaries as ffmpeg
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

# Initialize ffmpeg_binaries module
ffmpeg.init()

def check_ffmpeg_installation():
    """检查FFmpeg是否已安装并可用"""
    try:
        # 使用ffmpeg_binaries运行ffmpeg命令
        result = ffmpeg.run_as_ffmpeg("-version")
        return True
    except Exception:
        return False

def get_ffmpeg_path():
    """获取FFmpeg可执行文件路径"""
    # 使用ffmpeg_binaries时，可以直接调用ffmpeg.run_as_ffmpeg
    # 这里返回一个标识符表示使用ffmpeg_binaries
    return "ffmpeg_binaries"

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

def add_audio_to_video(video_path: str, audio_path: str, output_dir: str) -> str:
    """
    将音频文件添加到视频文件中
    
    参数:
        video_path: str - 输入视频的路径
        audio_path: str - 输入音频的路径
        output_dir: str - 输出视频的目录路径
        
    返回:
        str: 处理后视频的路径，失败返回None
    """
    output_path = None
    
    try:
        # 检查输入文件是否存在
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return None
            
        if not os.path.exists(audio_path):
            logger.error(f"音频文件不存在: {audio_path}")
            return None
            
        # 确保输出目录存在
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"创建输出目录失败: {str(e)}")
            return None
            
        # 生成输出文件路径
        video_filename = os.path.basename(video_path)
        output_filename = f"with_audio_{video_filename}"
        output_path = os.path.join(output_dir, output_filename)

        # 构建ffmpeg命令，以视频时长为准
        logger.info("开始合成视频和音频（以视频时长为准）...")
        
        # 构建命令参数列表
        args = [
            "-i", video_path,      # 输入视频
            "-i", audio_path,      # 输入音频
            "-c:v", "copy",        # 视频流复制
            "-c:a", "aac",         # 音频编码为AAC
            "-b:a", "320k",        # 音频比特率
            "-shortest",           # 以最短流为准（即视频长度）
            "-loglevel", "error",  # 只显示错误，减少输出
            "-y",                  # 覆盖输出文件
            output_path
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
            logger.info(f"视频音频合成完成，已保存至: {output_path}")
            return output_path
        else:
            logger.error("合成失败，输出文件不存在")
            return None
            
    except Exception as e:
        import traceback
        logger.error(f"处理视频时发生错误: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        
        # 清理失败的输出文件
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"已删除失败的输出文件: {output_path}")
            except Exception as del_e:
                logger.error(f"删除失败的输出文件时出错: {str(del_e)}")
        return None

if __name__ == "__main__":
    add_audio_to_video("/Users/chaiyapeng/Desktop/video/task_114/no_music_vides/286.mp4",
                       "/Users/chaiyapeng/Downloads/music/NoTitle.mp3", 
                       "/Users/chaiyapeng/Desktop/video/task_114/videos")