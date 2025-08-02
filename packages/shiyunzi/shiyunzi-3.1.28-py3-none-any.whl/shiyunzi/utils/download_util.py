import requests
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)
def download_image(image_url: str, save_path: str):
    logger.info(f"开始下载图片: {image_url}")
    try:
        response = requests.get(image_url)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"下载图片失败: {e}")
        return False

def download_video(video_url: str, save_path: str):
    try:
        logger.info(f"开始下载视频: {video_url}")
        response = requests.get(video_url, timeout=15)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"下载视频失败: {e}")
        return False