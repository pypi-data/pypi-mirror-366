import asyncio
import os
from shiyunzi.utils.log_util import get_logger
from shiyunzi.jimeng.jimeng_login_service import JimengLoginService
from shiyunzi.jimeng.jimeng_image_service import JimengImageService, Resolution
from shiyunzi.jimeng.jimeng_video_service import JimengVideoService, VideoResolution, VideoLength

logger = get_logger(__name__)

class JimengService:
    """即梦国内版服务统一入口"""
    def __init__(self, headless: bool = False):
        # 是否使用无头模式
        self.headless = headless
        # 创建登录服务
        self.login_service = JimengLoginService(headless=headless)
        # 创建图片生成服务
        self.image_service = None
        # 创建视频生成服务
        self.video_service = None
        # 获取脚本所在目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cookies_path = os.path.join(self.script_dir, "cookies.json")
    
    async def init(self):
        """初始化服务"""
        try:
            # 初始化浏览器
            if not await self.login_service.init_browser():
                logger.error("浏览器初始化失败")
                return False
                
            # 如果没有登录，先登录
            if not os.path.exists(self.login_service.cookies_path):
                if not await self.login_service.login():
                    logger.error("登录失败")
                    return False
            
            # 初始化图片生成服务
            self.image_service = JimengImageService(self.login_service)
            
            # 初始化视频生成服务
            self.video_service = JimengVideoService(self.login_service, headless=self.headless)
            
            logger.info("即梦服务初始化成功")
            return True
        except Exception as e:
            logger.error(f"初始化服务时出错: {str(e)}")
            return False
    
    async def close(self):
        """关闭服务"""
        await self.login_service.close()
        logger.info("即梦服务已关闭")
    
    async def generate_image(self, prompt: str, resolution: Resolution = Resolution.RATIO_1_1):
        """
        生成图片
        :param prompt: 提示词
        :param resolution: 分辨率，支持多种比例选择
        :return: 是否成功
        """
        if not self.image_service:
            logger.error("图片生成服务未初始化")
            return False
        
        return await self.image_service.generate_image(prompt, resolution)
    
    async def generate_video(self, 
                          prompt: str, 
                          resolution: VideoResolution = VideoResolution.RATIO_16_9, 
                          length: VideoLength = VideoLength.SHORT,
                          reference_image: str = None):
        """
        生成视频
        :param prompt: 提示词
        :param resolution: 视频分辨率
        :param length: 视频长度
        :param reference_image: 参考图片路径（可选）
        :return: 是否成功
        """
        if not self.video_service:
            logger.error("视频生成服务未初始化")
            return False
        
        return await self.video_service.generate_video(prompt, resolution, length, reference_image=reference_image)

async def main():
    """主函数示例"""
    # 使用无头模式创建服务
    service = JimengService(headless=True)
    try:
        # 初始化服务
        if await service.init():
            # 测试生成图片
            image_prompt = "一个美丽的日落场景，金色的阳光洒在海面上"
            if await service.generate_image(image_prompt, Resolution.RATIO_16_9):
                logger.info("图片生成和下载完成")
            else:
                logger.error("图片生成或下载失败")
            
            # 测试生成视频
            video_prompt = "一个美丽的日落场景，金色的阳光洒在海面上，波光粼粼，远处有帆船缓缓驶过"
            # 使用参考图片
            reference_image = os.path.join(service.script_dir, "sample_image.jpg")  # 示例图片路径
            if await service.generate_video(
                video_prompt, 
                VideoResolution.RATIO_16_9, 
                VideoLength.SECONDS_5, 
                reference_image=reference_image
            ):
                logger.info("视频生成和下载完成")
            else:
                logger.error("视频生成或下载失败")
    finally:
        # 确保服务被关闭
        await service.close()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
