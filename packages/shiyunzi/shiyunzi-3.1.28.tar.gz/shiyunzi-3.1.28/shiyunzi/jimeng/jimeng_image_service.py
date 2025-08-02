import asyncio
import subprocess
import os
import json
import time
import re
import requests
from enum import Enum
from typing import Optional, Dict, Any, List
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Response
from shiyunzi.utils.log_util import get_logger
from shiyunzi.jimeng.jimeng_login_service import JimengLoginService

logger = get_logger(__name__)

class Resolution(Enum):
    RATIO_21_9 = "21:9"
    RATIO_16_9 = "16:9"  # 横屏
    RATIO_3_2 = "3:2"
    RATIO_4_3 = "4:3"
    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_2_3 = "2:3"
    RATIO_9_16 = "9:16"  # 竖屏

class JimengImageService:
    """即梦国内版图片生成服务"""
    def __init__(self, login_service: Optional[JimengLoginService] = None):
        # 如果提供了登录服务，则使用它，否则创建一个新的
        self.login_service = login_service if login_service else JimengLoginService()
        
        self.base_url = "https://jimeng.jianying.com"
        self.generate_url = f"{self.base_url}/ai-tool/generate?type=image"
        self.generate_api = "https://jimeng.jianying.com/mweb/v1/aigc_draft/generate"
        self.history_api = "https://jimeng.jianying.com/mweb/v1/get_history_by_ids"
        
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
                # 检查分辨率按钮
                resolution_btn = await self.login_service.page.wait_for_selector(
                    'button:has-text("1:1")',
                    timeout=10000,
                    state='visible'
                )
                if resolution_btn:
                    logger.info("找到分辨率按钮")
            except TimeoutError:
                logger.error("等待分辨率按钮超时")
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
        """导航到生成页面"""
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

            # 跳转到生成页面
            logger.info(f"正在跳转到生成页面: {self.generate_url}")
            
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
            logger.error(f"导航到生成页面时出错: {str(e)}")
            return False

    async def select_resolution(self, resolution: Resolution):
        """选择图片分辨率"""
        try:
            # 先点击分辨率按钮（默认显示的1:1按钮）
            resolution_button = await self.login_service.page.wait_for_selector('button:has-text("1:1")')
            await resolution_button.click()
            logger.info("已点击分辨率选择按钮")
            
            # 等待弹出框出现
            await asyncio.sleep(1)
            
            resolution_value = resolution.value
            
            # 根据不同的分辨率使用不同的定位策略
            if resolution == Resolution.RATIO_9_16:
                # 竖屏 9:16，使用特定的SVG路径模式
                selector = 'div.radio-content-YzIxZV:has(path[d*="5.707 5.325"])'
            elif resolution == Resolution.RATIO_16_9:
                # 横屏 16:9，使用特定的SVG路径模式
                selector = 'div.radio-content-YzIxZV:has(path[d*="1.924 9.706"])'
            else:
                # 其他分辨率使用文本定位
                selector = f'div.radio-content-YzIxZV:has-text("{resolution_value}")'
            
            # 等待选项出现并点击
            resolution_option = await self.login_service.page.wait_for_selector(selector)
            if resolution_option:
                await resolution_option.click()
                logger.info(f"已选择分辨率: {resolution_value}")
                # 等待选择生效
                await asyncio.sleep(0.5)
                return True
            else:
                logger.error(f"未找到分辨率选项: {resolution_value}")
                return False
            
        except Exception as e:
            logger.error(f"选择分辨率失败: {str(e)}")
            return False

    async def wait_for_generation_complete(self, timeout: int = 300):
        """
        等待图片生成完成
        :param timeout: 超时时间（秒）
        :return: 是否成功生成
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查进度标识是否存在
                progress_badge = await self.login_service.page.query_selector('div.progress-badge-Wyx18r')
                if not progress_badge:
                    # 如果进度标识不存在，说明生成完成
                    logger.info("图片生成完成")
                    return True
                
                # 获取进度文本
                if progress_badge:
                    progress_text = await progress_badge.text_content()
                    logger.info(f"当前进度: {progress_text}")
                
                # 等待一段时间再检查
                await asyncio.sleep(1)
            
            logger.error(f"图片生成超时（{timeout}秒）")
            return False
            
        except Exception as e:
            logger.error(f"监控生成进度时出错: {str(e)}")
            return False

    async def get_hd_image_url(self):
        """获取高清图片URL"""
        try:
            # 等待图片容器加载
            container = await self.login_service.page.wait_for_selector('.container-EdniD0')
            if not container:
                logger.error("未找到图片容器")
                return None

            # 检查是否是超清图片
            meta_right = await container.query_selector('.metaRight-fF8GZJ')
            if meta_right:
                meta_text = await meta_right.text_content()
                if meta_text.strip() != '超清':
                    logger.error("不是超清图片")
                    return None

            # 获取图片元素
            img_element = await container.query_selector('.image-mh68Se')
            if not img_element:
                logger.error("未找到图片元素")
                return None

            # 获取图片URL
            src = await img_element.get_attribute('src')
            if not src:
                logger.error("未找到图片URL")
                return None

            # 确保URL包含高清参数
            if 'aigc_resize:2400:2400' not in src:
                # 尝试将URL转换为高清版本
                src = re.sub(r'aigc_resize:\d+:\d+', 'aigc_resize:2400:2400', src)
                if 'aigc_resize:2400:2400' not in src:
                    src = src.replace('~tplv', '~aigc_resize:2400:2400~tplv')

            logger.info(f"找到高清图片URL: {src}")
            return src

        except Exception as e:
            logger.error(f"获取高清图片URL时出错: {str(e)}")
            return None

    async def wait_for_generate_response(self, generate_button) -> Optional[str]:
        """等待生成接口的响应，获取submit_id"""
        try:
            logger.info(f"开始监听生成接口: {self.generate_api}")
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

    async def get_image_urls_by_submit_id(self, submit_id: str) -> list:
        """通过submit_id获取图片URL列表"""
        try:
            # 准备请求数据
            payload = {
                "submit_ids": [submit_id]
            }

            logger.info(f"开始监听历史记录接口: {self.history_api}")
            # 先开始监听响应
            async with self.login_service.page.expect_response(
                lambda response: self.history_api in response.url
            ) as response_info:
                # 发送POST请求
                await self.login_service.page.request.post(
                    self.history_api,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"}
                )
                logger.info("已发送历史记录请求")
                
                # 等待响应
                response = await response_info.value
                logger.info(f"收到历史记录响应，状态码: {response.status}")

                if response.status != 200:
                    logger.error(f"历史记录接口返回错误状态码: {response.status}")
                    return []

                try:
                    # 解析响应数据
                    response_json = await response.json()
                    data = response_json.get('data', {})
                    
                    # 获取item_list
                    item_list = data.get(submit_id, {}).get('item_list', [])
                    image_urls = []
                    
                    for item in item_list:
                        # 获取large_images列表
                        large_images = item.get('image', {}).get('large_images', [])
                        if large_images:
                            # 获取第一个large_image的URL
                            image_url = large_images[0].get('image_url')
                            if image_url:
                                image_urls.append(image_url)
                                logger.info(f"找到图片URL: {image_url}")
                    
                    logger.info(f"找到 {len(image_urls)} 个图片URL")
                    return image_urls
                except Exception as e:
                    logger.error(f"解析历史记录响应数据失败: {str(e)}")
                    return []
            
        except Exception as e:
            logger.error(f"获取图片URL时出错: {str(e)}")
            return []

    async def remove_watermark(self, image_path: str) -> bool:
        """
        使用ffmpeg去除图片上的"AI生成"水印
        :param image_path: 图片路径
        :return: 是否成功去除水印
        """
        try:
            # 获取原始文件名和扩展名
            file_dir, file_name = os.path.split(image_path)
            file_base, file_ext = os.path.splitext(file_name)
            output_path = os.path.join(file_dir, f"{file_base}_nowm{file_ext}")
            
            # 检查ffmpeg是否安装
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.error("ffmpeg未安装或无法访问，跳过去水印")
                return False
                
            # 首先获取图片尺寸
            try:
                ffprobe_cmd = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height", "-of", "json", image_path
                ]
                result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
                
                # 解析图片尺寸
                info = json.loads(result.stdout)
                width = info["streams"][0]["width"]
                height = info["streams"][0]["height"]
            except Exception as e:
                logger.error(f"获取图片尺寸失败: {str(e)}")
                return False
            
            # 水印位于左上角，约占图片宽度的20%，高度的10%
            watermark_width = int(width * 0.2)
            watermark_height = int(height * 0.1)
            
            # 使用boxblur滤镜处理水印区域
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", image_path,
                "-vf", f"boxblur=10:10:0:0:0:0:enable='between(X,0,{watermark_width})*(between(Y,0,{watermark_height}))'",
                output_path
            ]
            
            logger.info(f"执行去水印命令: {' '.join(ffmpeg_cmd)}")
            try:
                # 执行ffmpeg命令
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
                
                # 检查输出文件是否存在
                if not os.path.exists(output_path):
                    logger.error(f"ffmpeg执行成功但输出文件不存在: {output_path}")
                    return False
                
                # 检查输出文件大小
                if os.path.getsize(output_path) == 0:
                    logger.error(f"ffmpeg生成的文件大小为0: {output_path}")
                    os.remove(output_path)  # 删除空文件
                    return False
                
                # 去水印成功后，用处理后的图片替换原图
                os.rename(output_path, image_path)
                
                logger.info(f"已成功去除水印: {image_path}")
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"ffmpeg执行失败: {e.stderr}")
                # 清理可能存在的输出文件
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False
            
        except Exception as e:
            logger.error(f"去除水印时出错: {str(e)}")
            # 清理可能存在的输出文件
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
            return False

    async def download_image(self, url: str, index: int = 0) -> bool:
        """下载单张图片"""
        try:
            # 设置下载路径
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # 使用原始URL中的扩展名
            ext = url.split('.')[-1].split('?')[0]
            download_path = os.path.join(
                self.download_dir,
                f"generated_image_{timestamp}_{index}.{ext}"
            )

            # 使用requests库直接下载图片
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"图片已保存到: {download_path}")
                
                # 下载成功后去除水印
                if await self.remove_watermark(download_path):
                    logger.info(f"已成功去除水印: {download_path}")
                else:
                    logger.warning(f"去除水印失败，但图片已下载: {download_path}")
                
                return True
            else:
                logger.error(f"下载图片失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"下载图片时出错: {str(e)}")
            return False

    async def generate_image(self, prompt: str, resolution: Resolution = Resolution.RATIO_1_1):
        """
        生成图片
        :param prompt: 提示词
        :param resolution: 分辨率，支持多种比例选择
        """
        try:
            # 导航到生成页面
            if not await self.navigate_to_generate_page():
                return False
            
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
            
            # 选择分辨率
            if not await self.select_resolution(resolution):
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
            
            # 循环检查生成结果
            max_retries = 60  # 最多等待60次
            retry_interval = 3  # 每次等待3秒
            
            for i in range(max_retries):
                # 获取图片URL列表
                image_urls = await self.get_image_urls_by_submit_id(submit_id)
                if image_urls:
                    logger.info("图片生成完成")
                    # 下载所有生成的图片
                    success = True
                    for idx, url in enumerate(image_urls):
                        if not await self.download_image(url, idx):
                            success = False
                    return success
                
                logger.info(f"等待生成完成，还需等待 {(max_retries-i)*retry_interval} 秒")
                await asyncio.sleep(retry_interval)
            
            logger.error("等待图片生成超时")
            return False
            
        except Exception as e:
            logger.error(f"生成图片过程出错: {str(e)}")
            return False

async def main():
    """主函数示例"""
    # 先创建登录服务
    login_service = JimengLoginService()
    try:
        # 初始化浏览器
        if not await login_service.init_browser():
            logger.error("浏览器初始化失败")
            return
            
        # 如果没有登录，先登录
        if not os.path.exists(login_service.cookies_path):
            if not await login_service.login():
                logger.error("登录失败")
                return
        
        # 创建图片生成服务
        image_service = JimengImageService(login_service)
        
        # 测试生成图片
        prompt = "一个美丽的日落场景，金色的阳光洒在海面上"
        # 使用16:9分辨率
        if await image_service.generate_image(prompt, Resolution.RATIO_16_9):
            logger.info("图片生成和下载完成")
        else:
            logger.error("图片生成或下载失败")
    finally:
        # 确保浏览器被关闭
        await login_service.close()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 