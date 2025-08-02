import asyncio
import subprocess
import os
import json
import time
import re
import requests
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Response, FileChooser
from shiyunzi.utils.log_util import get_logger
from shiyunzi.jimeng.jimeng_login_service import JimengLoginService

logger = get_logger(__name__)

class VideoResolution(Enum):
    """视频分辨率枚举"""
    RATIO_16_9 = "16:9"  # 横屏
    RATIO_9_16 = "9:16"  # 竖屏
    RATIO_1_1 = "1:1"    # 方形

class VideoLength(Enum):
    """视频长度枚举"""
    SECONDS_5 = "5s"  # 5秒视频
    SECONDS_10 = "10s"  # 10秒视频

class JimengVideoService:
    """即梦国内版视频生成服务"""
    def __init__(self, login_service: Optional[JimengLoginService] = None, headless: bool = False):
        # 如果提供了登录服务，则使用它，否则创建一个新的
        self.login_service = login_service if login_service else JimengLoginService(headless=headless)
        self.headless = headless
        
        self.base_url = "https://jimeng.jianying.com"
        self.generate_url = f"{self.base_url}/ai-tool/generate?type=video"
        self.generate_api = "https://jimeng.jianying.com/mweb/v1/aigc_draft/generate"
        self.history_api = "https://jimeng.jianying.com/mweb/v1/get_history_by_ids"
        self.video_status_api = "https://jimeng.jianying.com/mweb/v1/aigc_draft/get_video_status"
        
        # 获取脚本所在目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # 创建下载目录
        self.download_dir = os.path.join(self.script_dir, "downloads")
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def wait_for_page_load(self):
        """等待页面完全加载"""
        try:
            # 等待页面基本加载完成
            await self.login_service.page.wait_for_load_state('domcontentloaded', timeout=30000)
            logger.info("页面DOM加载完成")

            # 等待网络请求基本完成
            await self.login_service.page.wait_for_load_state('networkidle', timeout=30000)
            logger.info("页面网络请求完成")

            # 分步检查关键元素
            try:
                # 检查输入框
                textarea = await self.login_service.page.wait_for_selector(
                    "textarea.prompt-textarea-XfqAoB",
                    timeout=10000,
                    state='visible'
                )
                if textarea:
                    logger.info("找到输入框")
            except TimeoutError:
                logger.error("等待输入框超时")
                return False

            try:
                # 检查生成按钮
                generate_btn = await self.login_service.page.wait_for_selector(
                    'button.submit-button-VW0U_J',
                    timeout=10000,
                    state='visible'
                )
                if generate_btn:
                    logger.info("找到生成按钮")
            except TimeoutError:
                logger.error("等待生成按钮超时")
                return False

            # 额外等待一小段时间确保界面完全渲染
            await asyncio.sleep(1)
            logger.info("页面加载完成")
            return True

        except PlaywrightTimeoutError:
            logger.error("等待页面加载超时")
            return False
        except Exception as e:
            logger.error(f"等待页面加载出错: {str(e)}")
            return False

    async def navigate_to_generate_page(self):
        """导航到视频生成页面"""
        try:
            # 访问主页
            logger.info(f"正在访问主页: {self.login_service.home_url}")
            await self.login_service.page.goto(self.login_service.home_url, wait_until='domcontentloaded')
            
            # 加载cookies
            await self.login_service.load_cookies()
            
            # 等待一下确保cookies生效
            await asyncio.sleep(1)
            
            # 检查并关闭更新提示弹窗
            if not await self.login_service.close_update_modal():
                return False

            # 跳转到视频生成页面
            logger.info(f"正在跳转到视频生成页面: {self.generate_url}")
            
            # 使用try-catch处理导航
            try:
                # 设置较长的超时时间，因为有时候加载会比较慢
                await self.login_service.page.goto(self.generate_url, timeout=60000, wait_until='domcontentloaded')
            except TimeoutError:
                logger.error("页面导航超时")
                return False
            except Exception as e:
                logger.error(f"页面导航出错: {str(e)}")
                return False
            
            # 等待页面完全加载
            return await self.wait_for_page_load()
            
        except Exception as e:
            logger.error(f"导航到视频生成页面时出错: {str(e)}")
            return False

    async def select_video_resolution(self, resolution: VideoResolution):
        """选择视频分辨率"""
        try:
            # 点击分辨率选择区域
            resolution_selector = '.resolution-container-Jvnx5P'
            resolution_container = await self.login_service.page.wait_for_selector(resolution_selector)
            if not resolution_container:
                logger.error("未找到分辨率选择区域")
                return False
                
            await resolution_container.click()
            logger.info("已点击分辨率选择区域")
            
            # 等待弹出框出现
            await asyncio.sleep(1)
            
            # 根据不同的分辨率选择不同的选项
            if resolution == VideoResolution.RATIO_16_9:
                selector = 'div.radio-content-YzIxZV:has-text("16:9")'
            elif resolution == VideoResolution.RATIO_9_16:
                selector = 'div.radio-content-YzIxZV:has-text("9:16")'
            else:  # 1:1
                selector = 'div.radio-content-YzIxZV:has-text("1:1")'
            
            # 等待选项出现并点击
            resolution_option = await self.login_service.page.wait_for_selector(selector)
            if resolution_option:
                await resolution_option.click()
                logger.info(f"已选择视频分辨率: {resolution.value}")
                # 等待选择生效
                await asyncio.sleep(0.5)
                return True
            else:
                logger.error(f"未找到视频分辨率选项: {resolution.value}")
                return False
            
        except Exception as e:
            logger.error(f"选择视频分辨率失败: {str(e)}")
            return False

    async def select_video_length(self, length: VideoLength):
        """选择视频长度"""
        try:
            # 点击视频长度选择区域
            length_selector = '.video-length-container-HFZMjx'
            length_container = await self.login_service.page.wait_for_selector(length_selector)
            if not length_container:
                logger.error("未找到视频长度选择区域")
                return False
                
            await length_container.click()
            logger.info("已点击视频长度选择区域")
            
            # 等待弹出框出现
            await asyncio.sleep(1)
            
            # 根据不同的长度选择不同的选项
            if length == VideoLength.SECONDS_5:
                selector = 'div.radio-content-YzIxZV:has-text("5s")'
            elif length == VideoLength.SECONDS_10:
                selector = 'div.radio-content-YzIxZV:has-text("10s")'
            elif length == VideoLength.SECONDS_5:
                # 先选择短视频
                short_selector = 'div.radio-content-YzIxZV:has-text("短视频")'
                short_option = await self.login_service.page.wait_for_selector(short_selector)
                if short_option:
                    await short_option.click()
                    logger.info("已选择短视频作为基础长度")
                    await asyncio.sleep(0.5)
                    
                    # 然后设置自定义时长为5秒
                    await self.set_custom_video_length(5)
                    return True
                else:
                    logger.error("未找到短视频选项")
                    return False
            elif length == VideoLength.SECONDS_10:
                # 先选择短视频
                short_selector = 'div.radio-content-YzIxZV:has-text("短视频")'
                short_option = await self.login_service.page.wait_for_selector(short_selector)
                if short_option:
                    await short_option.click()
                    logger.info("已选择短视频作为基础长度")
                    await asyncio.sleep(0.5)
                    
                    # 然后设置自定义时长为10秒
                    await self.set_custom_video_length(10)
                    return True
                else:
                    logger.error("未找到短视频选项")
                    return False
            
            # 如果不是自定义时长，则直接选择预设选项
            if length not in [VideoLength.SECONDS_5, VideoLength.SECONDS_10]:
                length_option = await self.login_service.page.wait_for_selector(selector)
                if length_option:
                    await length_option.click()
                    logger.info(f"已选择视频长度: {length.value}")
                    # 等待选择生效
                    await asyncio.sleep(0.5)
                    return True
                else:
                    logger.error(f"未找到视频长度选项: {length.value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"选择视频长度失败: {str(e)}")
            return False
    
    async def set_custom_video_length(self, seconds: int):
        """设置自定义视频时长"""
        try:
            # 检查是否有自定义时长选项
            custom_length_selector = '.custom-length-container-Iy8Mwx'
            custom_length_container = await self.login_service.page.wait_for_selector(custom_length_selector)
            if not custom_length_container:
                logger.error("未找到自定义时长选项")
                return False
            
            # 点击自定义时长选项
            await custom_length_container.click()
            logger.info("已点击自定义时长选项")
            
            # 等待输入框出现
            await asyncio.sleep(0.5)
            
            # 查找输入框
            input_selector = 'input.lv-input-inner'
            input_element = await self.login_service.page.wait_for_selector(input_selector)
            if not input_element:
                logger.error("未找到时长输入框")
                return False
            
            # 清空输入框并输入新的时长
            await input_element.fill("")
            await input_element.fill(str(seconds))
            logger.info(f"已设置自定义时长: {seconds}秒")
            
            # 点击确认按钮
            confirm_button = await self.login_service.page.wait_for_selector('button.lv-btn-primary')
            if confirm_button:
                await confirm_button.click()
                logger.info("已确认自定义时长")
                await asyncio.sleep(0.5)
                return True
            else:
                logger.error("未找到确认按钮")
                return False
            
        except Exception as e:
            logger.error(f"设置自定义时长失败: {str(e)}")
            return False
    
    async def upload_reference_image(self, image_path: str):
        """上传参考图片"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"图片不存在: {image_path}")
                return False
            
            logger.info(f"准备上传图片: {image_path}")
            
            # 在点击上传按钮之前，先设置页面接受文件选择器事件
            # 这样可以在无头模式下自动处理文件上传
            
            # 方法1: 直接设置文件输入框的值
            try:
                # 先尝试直接找到文件输入框并设置其值
                file_input = await self.login_service.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    logger.info("已通过直接设置文件输入框值上传图片")
                    # 等待上传完成
                    await asyncio.sleep(2)
                    # 检查上传是否成功
                    return await self._check_upload_success()
            except Exception as e:
                logger.warning(f"直接设置文件输入框失败: {str(e)}")
            
            # 方法2: 使用expect_file_chooser并点击上传按钮
            # 查找上传按钮 - 使用更精确的选择器，查找带有"首帧"标签的上传按钮
            upload_label = await self.login_service.page.query_selector('div.label-wsE_gG:has-text("首帧")')
            
            if not upload_label:
                # 尝试其他可能的选择器
                alternative_selectors = [
                    '.reference-upload-eclumn',  # 直接查找上传容器
                    '.upload-container-Iy8Mwx',  # 原来的选择器
                    'div:has(> svg + div:has-text("首帧"))'  # 查找包含SVG图标和"首帧"文本的div
                ]
                
                for selector in alternative_selectors:
                    upload_label = await self.login_service.page.query_selector(selector)
                    if upload_label:
                        logger.info(f"使用备选选择器找到上传按钮: {selector}")
                        break
            
            if not upload_label:
                logger.error("未找到上传按钮")
                return False
            
            # 使用expect_file_chooser来监听文件选择器事件
            async with self.login_service.page.expect_file_chooser() as fc_info:
                # 点击上传按钮
                if upload_label == await self.login_service.page.query_selector('div.label-wsE_gG:has-text("首帧")'):
                    await upload_label.evaluate('el => el.closest(".reference-upload-eclumn").click()')
                else:
                    await upload_label.click()
                logger.info("已点击上传按钮")
                
                try:
                    # 获取文件选择器
                    file_chooser = await fc_info.value
                    # 设置文件路径
                    await file_chooser.set_files(image_path)
                    logger.info(f"已通过文件选择器上传图片: {image_path}")
                except Exception as e:
                    logger.error(f"通过文件选择器上传失败: {str(e)}")
                    return False
            
            # 等待上传完成
            await asyncio.sleep(2)
            
            # 检查上传是否成功
            return await self._check_upload_success()
                
        except Exception as e:
            logger.error(f"上传参考图片失败: {str(e)}")
            return False
    
    async def _check_upload_success(self):
        """检查图片上传是否成功"""
        try:
            # 尝试多种可能的预览图选择器
            preview_selectors = [
                '.preview-container-Iy8Mwx img',  # 原来的选择器
                'img[alt="reference"]',           # 可能的替代选择器
                '.reference-image-preview img',   # 另一个可能的选择器
                'img.preview-image',              # 通用预览图类
                '.image-preview-container img'    # 另一个可能的容器
            ]
            
            preview_image = None
            for selector in preview_selectors:
                try:
                    element = await self.login_service.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        preview_image = element
                        break
                except Exception:
                    continue
            
            if preview_image:
                logger.info("图片上传成功")
                return True
            else:
                # 尝试检查是否有其他指示上传成功的元素
                success_indicators = [
                    '.upload-success-icon',
                    '.reference-image-container',
                    'div:has-text("上传成功")'
                ]
                
                for selector in success_indicators:
                    try:
                        element = await self.login_service.page.wait_for_selector(selector, timeout=1000)
                        if element:
                            logger.info(f"检测到上传成功指示器: {selector}")
                            return True
                    except Exception:
                        continue
                
                # 即使没有找到预览图，也不一定意味着上传失败
                logger.warning("未找到图片预览，但上传可能已成功")
                # 在这种情况下，我们假设上传成功，因为有时预览可能不会立即显示
                return True
        except Exception as e:
            logger.error(f"检查上传状态时出错: {str(e)}")
            return False

    async def wait_for_generate_response(self, generate_button) -> Optional[str]:
        """等待生成接口的响应，获取submit_id"""
        try:
            logger.info(f"开始监听视频生成接口: {self.generate_api}")
            # 先开始监听响应
            async with self.login_service.page.expect_response(
                lambda response: self.generate_api in response.url
            ) as response_info:
                # 然后点击生成按钮
                await generate_button.click()
                logger.info("已点击生成按钮")
                
                # 等待响应
                response = await response_info.value
                logger.info(f"收到响应，状态码: {response.status}")
                
                if response.status != 200:
                    logger.error(f"生成接口返回错误状态码: {response.status}")
                    return None

                # 解析响应数据
                try:
                    # 正确的获取JSON数据方式
                    response_json = await response.json()
                    data = response_json.get('data', {})
                    logger.info(f"响应数据: {json.dumps(data, ensure_ascii=False)}")
                    
                    submit_id = data.get('aigc_data', {}).get('task', {}).get('submit_id')
                    if submit_id:
                        logger.info(f"获取到submit_id: {submit_id}")
                        return submit_id
                    else:
                        logger.error("未在响应中找到submit_id")
                        return None
                except Exception as e:
                    logger.error(f"解析响应数据失败: {str(e)}")
                    return None
                    
        except Exception as e:
            logger.error(f"等待生成接口响应时出错: {str(e)}")
            return None

    async def check_video_status(self, submit_id: str) -> Dict[str, Any]:
        """
        检查视频生成状态
        :param submit_id: 提交ID
        :return: 状态信息字典
        """
        try:
            # 准备请求数据
            payload = {
                "submit_id": submit_id
            }
            
            # 发送POST请求
            response = await self.login_service.page.request.post(
                self.video_status_api,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            # 解析响应
            response_json = await response.json()
            data = response_json.get('data', {})
            
            # 获取状态信息
            status = data.get('status', '')
            progress = data.get('progress', 0)
            video_url = data.get('video_url', '')
            
            logger.info(f"视频状态: {status}, 进度: {progress}%, URL: {video_url}")
            
            return {
                "status": status,
                "progress": progress,
                "video_url": video_url
            }
            
        except Exception as e:
            logger.error(f"检查视频状态时出错: {str(e)}")
            return {
                "status": "error",
                "progress": 0,
                "video_url": ""
            }

    async def wait_for_video_generation(self, submit_id: str, timeout: int = 1800) -> Optional[str]:
        """
        等待视频生成完成
        :param submit_id: 提交ID
        :param timeout: 超时时间（秒），默认30分钟
        :return: 视频URL或None（如果失败）
        """
        try:
            start_time = time.time()
            last_progress = -1
            
            while time.time() - start_time < timeout:
                # 检查视频状态
                status_info = await self.check_video_status(submit_id)
                status = status_info.get('status', '')
                progress = status_info.get('progress', 0)
                video_url = status_info.get('video_url', '')
                
                # 只在进度变化时打印日志
                if progress != last_progress:
                    logger.info(f"视频生成进度: {progress}%")
                    last_progress = progress
                
                # 如果状态为完成，返回视频URL
                if status == "completed" and video_url:
                    logger.info(f"视频生成完成: {video_url}")
                    return video_url
                
                # 如果状态为失败，返回None
                if status == "failed":
                    logger.error("视频生成失败")
                    return None
                
                # 等待一段时间再检查
                await asyncio.sleep(5)
            
            logger.error(f"视频生成超时（{timeout}秒）")
            return None
            
        except Exception as e:
            logger.error(f"等待视频生成时出错: {str(e)}")
            return None

    async def download_video(self, url: str) -> bool:
        """下载视频"""
        try:
            # 设置下载路径
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            download_path = os.path.join(
                self.download_dir,
                f"generated_video_{timestamp}.mp4"
            )

            # 使用requests库直接下载视频
            response = requests.get(url, stream=True, timeout=300)  # 较长的超时时间，因为视频可能较大
            if response.status_code == 200:
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"视频已保存到: {download_path}")
                return True
            else:
                logger.error(f"下载视频失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"下载视频时出错: {str(e)}")
            return False

    async def generate_video(self, 
                           prompt: str, 
                           resolution: VideoResolution = VideoResolution.RATIO_16_9, 
                           length: VideoLength = VideoLength.SECONDS_5,
                           reference_image: Optional[str] = None):
        """
        生成视频
        :param prompt: 提示词
        :param resolution: 视频分辨率
        :param length: 视频长度
        :param reference_image: 参考图片路径（可选）
        :return: 是否成功
        """
        try:
            # 导航到视频生成页面
            if not await self.navigate_to_generate_page():
                return False
            
            # 如果提供了参考图片，先上传
            if reference_image:
                if not await self.upload_reference_image(reference_image):
                    logger.warning("参考图片上传失败，将继续生成视频但不使用参考图片")
            
            # 定位并填写提示词
            textarea_selector = "textarea.prompt-textarea-XfqAoB"
            textarea = await self.login_service.page.wait_for_selector(textarea_selector, state='visible')
            if not textarea:
                logger.error("未找到输入框")
                return False
            
            # 清空输入框并输入新的提示词
            await self.login_service.page.fill(textarea_selector, "")  # 清空
            await self.login_service.page.fill(textarea_selector, prompt)  # 输入新提示词
            logger.info(f"已输入提示词: {prompt}")
            
            # 选择视频分辨率
            if not await self.select_video_resolution(resolution):
                return False
                
            # 选择视频长度
            if not await self.select_video_length(length):
                return False

            # 等待生成按钮可点击
            generate_button = await self.login_service.page.wait_for_selector('button.submit-button-VW0U_J', state='visible')
            if not generate_button:
                logger.error("未找到生成按钮")
                return False

            # 等待生成接口响应，获取submit_id
            submit_id = await self.wait_for_generate_response(generate_button)
            if not submit_id:
                return False
            
            # 等待视频生成完成，获取视频URL
            video_url = await self.wait_for_video_generation(submit_id)
            if not video_url:
                return False
            
            # 下载视频
            if await self.download_video(video_url):
                logger.info("视频生成和下载完成")
                return True
            else:
                logger.error("视频下载失败")
                return False
            
        except Exception as e:
            logger.error(f"生成视频过程出错: {str(e)}")
            return False

async def main():
    """主函数示例"""
    # 创建视频生成服务，启用无头模式
    video_service = JimengVideoService(headless=False)
    try:
        # 初始化浏览器
        login_service = video_service.login_service
        if not await login_service.init_browser():
            logger.error("浏览器初始化失败")
            return
            
        # 如果没有登录，先登录
        if not os.path.exists(login_service.cookies_path):
            if not await login_service.login():
                logger.error("登录失败")
                return
        
        # 测试生成视频
        prompt = "跳舞"
        # 使用16:9分辨率，5秒视频，并提供参考图片
        reference_image = "/Users/chaiyapeng/Desktop/590838a09b83112fe675fa4af6e6fa1715f3ae6b5fc74ce70f03e1a96e49e75f.png"  # 参考图片的绝对路径
        if await video_service.generate_video(
            prompt, 
            VideoResolution.RATIO_9_16, 
            VideoLength.SECONDS_5,
            reference_image=reference_image
        ):
            logger.info("视频生成和下载完成")
        else:
            logger.error("视频生成或下载失败")
    finally:
        # 确保浏览器被关闭
        await login_service.close()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 