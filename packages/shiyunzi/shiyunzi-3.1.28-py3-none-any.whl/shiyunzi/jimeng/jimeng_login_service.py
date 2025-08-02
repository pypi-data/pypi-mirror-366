import asyncio
import os
import json
import time
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

class JimengLoginService:
    """即梦国内版登录服务"""
    def __init__(self, headless: bool = False):
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless  # 是否使用无头模式
        self.base_url = "https://jimeng.jianying.com"
        self.login_url = f"{self.base_url}/ai-tool/login"
        self.home_url = f"{self.base_url}/ai-tool/home"
        # 获取脚本所在目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cookies_path = os.path.join(self.script_dir, "cookies.json")
    
    @staticmethod
    def get_chrome_path():
        """获取 Chrome 浏览器路径"""
        if sys.platform == "darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            ]
        elif sys.platform == "win32":  # Windows
            paths = [
                os.path.expandvars("%ProgramFiles%/Google/Chrome/Application/chrome.exe"),
                os.path.expandvars("%ProgramFiles(x86)%/Google/Chrome/Application/chrome.exe"),
                os.path.expandvars("%LocalAppData%/Google/Chrome/Application/chrome.exe")
            ]
        else:  # Linux
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]

        for path in paths:
            if os.path.exists(path):
                logger.info(f"找到 Chrome 浏览器: {path}")
                return path
        
        logger.error("未找到 Chrome 浏览器")
        return None

    async def init_browser(self):
        """初始化浏览器"""
        try:
            chrome_path = self.get_chrome_path()
            if not chrome_path:
                raise Exception("请先安装 Google Chrome 浏览器")

            playwright = await async_playwright().start()
            # 启动Chrome浏览器
            browser_args = ['--start-maximized']
            if self.headless:
                # 在无头模式下添加额外参数以提高稳定性
                browser_args.extend([
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox'
                ])
            
            self.browser = await playwright.chromium.launch(
                headless=self.headless,  # 根据设置决定是否显示浏览器界面
                args=browser_args,
                channel='chrome',  # 使用Chrome而不是Chromium
                executable_path=chrome_path  # 指定Chrome路径
            )

            # 创建上下文
            context_options = {
                'viewport': None,  # 禁用视口大小限制
                'no_viewport': True  # 使用实际窗口大小
            }
            
            # 在无头模式下设置固定视口大小
            if self.headless:
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080}  # 设置固定视口大小
                }
                
            self.context = await self.browser.new_context(**context_options)
            
            # 创建新页面
            self.page = await self.context.new_page()
            
            # 在无头模式下，设置用户代理以避免被检测
            if self.headless:
                await self.page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
            
            logger.info(f"Chrome浏览器初始化成功，无头模式: {self.headless}")
            return True
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            return False

    async def save_cookies(self):
        """保存cookies到文件"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.info(f"Cookies已保存到: {self.cookies_path}")
            return True
        except Exception as e:
            logger.error(f"保存Cookies失败: {str(e)}")
            return False

    async def load_cookies(self):
        """从文件加载cookies"""
        try:
            if os.path.exists(self.cookies_path):
                with open(self.cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info("成功加载Cookies")
                return True
        except Exception as e:
            logger.error(f"加载Cookies失败: {str(e)}")
        return False

    async def check_login_status(self):
        """检查是否已登录"""
        try:
            current_url = self.page.url
            return current_url.startswith(self.home_url)
        except Exception:
            return False

    async def login(self):
        """登录剪映网站"""
        try:
            # 访问登录页面
            logger.info(f"正在访问登录页面: {self.login_url}")
            await self.page.goto(self.login_url)
            
            if self.headless:
                logger.warning("无头模式下无法进行交互式登录，请确保已有有效的cookies文件")
                return False
            
            # 设置开始时间
            start_time = time.time()
            check_interval = 1  # 每秒检查一次
            timeout = 180  # 180秒超时
            
            logger.info("等待用户登录中...")
            while time.time() - start_time < timeout:
                # 检查当前URL是否是home页面
                if await self.check_login_status():
                    logger.info("登录成功！")
                    # 保存cookies
                    await self.save_cookies()
                    return True
                
                # 等待一段时间再检查
                await asyncio.sleep(check_interval)
            
            logger.error("登录超时")
            return False
            
        except Exception as e:
            logger.error(f"登录过程出错: {str(e)}")
            return False

    async def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时发生错误: {str(e)}")

    async def close_update_modal(self):
        """检查并关闭更新提示弹窗"""
        try:
            # 等待弹窗出现（设置较短的超时时间，因为弹窗可能不存在）
            modal = await self.page.wait_for_selector('div[role="dialog"]', timeout=5000)
            if modal:
                # 检查是否包含特定文本，确认是更新提示弹窗
                modal_text = await modal.text_content()
                if "全新上线图片3.1模型" in modal_text:
                    # 点击关闭按钮
                    close_button = await self.page.wait_for_selector('span.lv-modal-close-icon')
                    if close_button:
                        await close_button.click()
                        logger.info("已关闭更新提示弹窗")
                        # 等待弹窗消失
                        await asyncio.sleep(1)
                    return True
        except PlaywrightTimeoutError:
            # 如果没有找到弹窗，说明不需要处理
            logger.info("未检测到更新提示弹窗")
            return True
        except Exception as e:
            logger.error(f"关闭更新提示弹窗时出错: {str(e)}")
            return False
        return True

async def main():
    """主函数示例"""
    # 创建登录服务，可以选择是否使用无头模式
    login_service = JimengLoginService(headless=False)
    try:
        # 初始化浏览器
        if await login_service.init_browser():
            # 如果没有登录，先登录
            if not os.path.exists(login_service.cookies_path):
                if await login_service.login():
                    logger.info("登录成功并保存了cookies")
                else:
                    logger.error("登录失败")
            else:
                logger.info("已有登录信息，无需重新登录")
    finally:
        # 确保浏览器被关闭
        await login_service.close()

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 