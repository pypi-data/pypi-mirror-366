from playwright.sync_api import sync_playwright
import re
import json
from typing import Dict, Optional, Callable
import subprocess
import sys
import os
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

class DoubaoCookieFetcher:
    def __init__(self, status_callback: Callable[[str], None] = None):
        self.device_id = None
        self.tea_uuid = None
        self.web_id = None
        self.cookies = None
        self.x_flow_trace = None
        self.room_id = None
        self._found_completion = False
        self._found_room = False
        self._found_cookies = False
        self.status_callback = status_callback
        self.page = None  # 保存页面引用，以便在获取接口时立即获取URL
        
    def _update_status(self, status: str):
        """更新状态，并通过回调函数通知"""
        logger.info(f"状态更新: {status}")
        if self.status_callback:
            self.status_callback(status)
    
    def _ensure_playwright_installed(self):
        """确保Playwright驱动程序已安装"""
        logger.info("检查Playwright驱动程序是否已安装")
        self._update_status("检查Playwright驱动程序...")
        try:
            # 安装Playwright浏览器和依赖
            logger.info("安装Playwright浏览器和依赖")
            self._update_status("安装Playwright浏览器和依赖...")
            
            # 安装chrome浏览器
            result1 = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chrome"],
                capture_output=True,
                text=True
            )
            if result1.returncode != 0:
                logger.warning(f"安装Chrome浏览器失败: {result1.stderr}")
            else:
                logger.info("Chrome浏览器安装成功")
            
            # 安装依赖
            result2 = subprocess.run(
                [sys.executable, "-m", "playwright", "install-deps", "chrome"],
                capture_output=True,
                text=True
            )
            if result2.returncode != 0:
                logger.warning(f"安装Chrome依赖失败: {result2.stderr}")
            else:
                logger.info("Chrome依赖安装成功")
                
            logger.info("Playwright浏览器安装完成")
            self._update_status("Playwright浏览器安装完成")
        except Exception as e:
            logger.error(f"安装Playwright驱动程序失败: {str(e)}")
            raise Exception(f"安装Playwright驱动程序失败: {str(e)}")
        
    def _handle_request(self, request):
        """处理请求，提取需要的信息"""
        # 第一个关键步骤：抓取samantha/chat/completion接口
        if 'samantha/chat/completion' in request.url:
            logger.info(f"第一个关键步骤：捕获到completion接口请求")
            self._update_status("第一个关键步骤：捕获到completion接口请求")
            
            # 解析URL参数
            try:
                url_params = dict(param.split('=') for param in request.url.split('?')[1].split('&'))
                self.device_id = url_params.get('device_id')
                self.tea_uuid = url_params.get('tea_uuid')
                self.web_id = url_params.get('web_id')
                
                # 获取完整的cookie
                if 'cookie' in request.headers:
                    cookies = request.headers.get('cookie', '')
                    if cookies:
                        self.cookies = cookies
                        self._found_cookies = True
                        logger.info(f"成功获取cookies，长度: {len(cookies)}")
                else:
                    logger.warning("请求头中未找到cookie字段")
                    # 尝试从其他字段获取cookie
                    for header_name, header_value in request.headers.items():
                        if "cookie" in header_name.lower():
                            logger.info(f"找到可能的cookie字段: {header_name}")
                            self.cookies = header_value
                            self._found_cookies = True
                            logger.info(f"从字段 {header_name} 获取cookies，长度: {len(header_value)}")
                
                # 获取x-flow-trace
                if 'x-flow-trace' in request.headers:
                    self.x_flow_trace = request.headers.get('x-flow-trace', '')
                
                # 从页面中获取document.cookie
                if self.page and (not self.cookies or len(self.cookies) < 100):
                    try:
                        # 立即从页面获取document.cookie
                        document_cookies = self.page.evaluate("() => document.cookie")
                        logger.info(f"从document.cookie获取的cookies长度: {len(document_cookies) if document_cookies else 0}")
                        
                        if document_cookies and (not self.cookies or len(document_cookies) > len(self.cookies)):
                            self.cookies = document_cookies
                            self._found_cookies = True
                            logger.info(f"使用document.cookie作为cookies，长度: {len(document_cookies)}")
                    except Exception as e:
                        logger.error(f"获取document.cookie失败: {str(e)}")
                
                # 输出所有获取到的信息（简化版）
                logger.info("=== 获取到的信息 ===")
                logger.info(f"device_id: {self.device_id}, tea_uuid: {self.tea_uuid}, web_id: {self.web_id}")
                logger.info(f"x-flow-trace长度: {len(self.x_flow_trace) if self.x_flow_trace else 0}")
                logger.info(f"cookies长度: {len(self.cookies) if self.cookies else 0}")
                logger.info("=== 信息获取完成 ===")
                
                self._found_completion = True
                logger.info("成功捕获completion接口信息")
                self._update_status("成功捕获completion接口信息")
                
                # 在获取到接口信息的同时，立即获取当前页面URL和提取room_id
                if self.page:
                    logger.info("立即获取当前页面URL和提取room_id")
                    self._check_url_for_room_id(self.page)
                
            except Exception as e:
                logger.error(f"解析completion接口失败: {str(e)}")
                
    def _get_cookies_from_application(self):
        """从浏览器的Application标签页获取cookie"""
        if not self.page:
            logger.warning("页面未初始化，无法获取cookies")
            return False
            
        try:
            logger.info("尝试从Application标签页获取cookies")
            
            # 执行JavaScript获取所有cookies
            cookies_js = """
            () => {
                try {
                    // 获取所有cookie
                    const allCookies = document.cookie;
                    
                    // 获取localStorage中可能存储的cookie
                    let localStorageCookies = "";
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        const value = localStorage.getItem(key);
                        localStorageCookies += `${key}=${value};`;
                    }
                    
                    return {
                        documentCookies: allCookies,
                        localStorageCookies: localStorageCookies
                    };
                } catch (e) {
                    return { error: e.toString() };
                }
            }
            """
            
            result = self.page.evaluate(cookies_js)
            
            if result and "documentCookies" in result and result["documentCookies"]:
                self.cookies = result["documentCookies"]
                self._found_cookies = True
                logger.info(f"成功从document.cookie获取cookies，长度: {len(self.cookies)}")
                return True
                
            return False
        except Exception as e:
            logger.error(f"从Application标签页获取cookie失败: {str(e)}")
            return False
            
    def _get_final_cookies(self):
        """在获取所有信息后等待3秒，再次获取完整的cookie并拼接"""
        try:
            logger.info("等待3秒后获取最终的cookies...")
            self.page.wait_for_timeout(3000)  # 等待3秒
            
            # 执行JavaScript获取所有cookies
            cookies_js = """
            () => {
                try {
                    // 获取所有cookie
                    return document.cookie;
                } catch (e) {
                    return "";
                }
            }
            """
            
            document_cookies = self.page.evaluate(cookies_js)
            logger.info(f"3秒后获取到的document.cookie长度: {len(document_cookies) if document_cookies else 0}")
            
            # 如果获取到了新的cookie，与之前的合并
            if document_cookies:
                # 解析现有cookie和新cookie
                existing_cookies = {}
                if self.cookies:
                    for cookie_pair in self.cookies.split(';'):
                        if '=' in cookie_pair:
                            key, value = cookie_pair.strip().split('=', 1)
                            existing_cookies[key] = value
                
                # 添加新cookie
                for cookie_pair in document_cookies.split(';'):
                    if '=' in cookie_pair:
                        key, value = cookie_pair.strip().split('=', 1)
                        if key not in existing_cookies:
                            existing_cookies[key] = value
                
                # 重新构建cookie字符串
                merged_cookies = '; '.join([f"{key}={value}" for key, value in existing_cookies.items()])
                
                if len(merged_cookies) > len(self.cookies or ""):
                    self.cookies = merged_cookies
                    logger.info(f"成功合并cookies，最终长度: {len(self.cookies)}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"获取最终cookies失败: {str(e)}")
            return False
            
    def _check_url_for_room_id(self, page):
        """第二个关键步骤：获取浏览器上方链接中的room_id"""
        current_url = page.url
        logger.info(f"当前浏览器地址: {current_url}")
        
        room_match = re.search(r'https://www\.doubao\.com/chat/(\d+)', current_url)
        if room_match:
            self.room_id = room_match.group(1)
            logger.info(f"从URL中提取到room_id: {self.room_id}")
            
            self._update_status(f"第二个关键步骤：从URL中捕获到room_id: {self.room_id}")
            self._found_room = True
            return True
        else:
            logger.info(f"URL中未找到room_id: {current_url}")
            return False
            
    def fetch(self) -> Dict[str, str]:
        """
        使用playwright自动抓取豆包网站的必要信息
        返回一个包含所有必要信息的字典
        """
        logger.info("开始抓取豆包配置信息")
        self._update_status("开始抓取豆包配置信息...")
        try:
            # 首先确保Playwright驱动程序已安装
            self._ensure_playwright_installed()
            
            with sync_playwright() as p:
                browser = None
                try:
                    # 首先尝试使用chrome
                    logger.info("尝试启动浏览器")
                    self._update_status("正在启动浏览器...")
                    
                    # 尝试多种方式启动Chrome
                    try:
                        # 方式1: 使用chrome channel
                        browser = p.chromium.launch(
                            headless=False,
                            channel="chrome"
                        )
                        logger.info("使用chrome channel启动成功")
                    except Exception as e1:
                        logger.warning(f"使用chrome channel启动失败: {str(e1)}")
                        
                        try:
                            # 方式2: 使用chrome实例
                            browser = p.chrome.launch(headless=False)
                            logger.info("使用chrome实例启动成功")
                        except Exception as e2:
                            logger.warning(f"使用chrome实例启动失败: {str(e2)}")
                            
                            # 方式3: 使用chromium
                            browser = p.chromium.launch(headless=False)
                            logger.info("使用chromium启动成功")
                    
                    if browser:
                        logger.info("浏览器启动成功")
                        self._update_status("浏览器启动成功")
                    else:
                        raise Exception("无法启动任何浏览器")
                        
                except Exception as e:
                    logger.error(f"启动浏览器失败: {str(e)}")
                    raise Exception(f"无法启动浏览器: {str(e)}")
                
                # 创建上下文并设置视口大小为全屏
                context = browser.new_context(
                    viewport=None  # 设置为None表示不限制视口大小，允许全屏
                )
                self.page = context.new_page()
                
                # 监听所有请求
                logger.info("设置请求监听")
                self.page.on('request', self._handle_request)
                
                # 访问豆包网站
                logger.info("访问豆包网站")
                self._update_status("正在访问豆包网站...")
                self.page.goto('https://www.doubao.com/chat/')
                logger.info("页面加载完成")
                self._update_status("页面加载完成，等待捕获信息...")
                
                # 设置浏览器全屏
                logger.info("设置浏览器全屏")
                self.page.evaluate("() => { document.documentElement.requestFullscreen(); }")
                
                # 添加提示信息，告知用户需要做什么
                self._update_status("请完成两个关键步骤：1. 发送消息触发API请求 2. 确保浏览器地址栏显示聊天页面URL")
                
                # 等待直到找到所需的所有信息或超时
                try:
                    logger.info("等待捕获所需信息")
                    timeout_counter = 0
                    max_timeout = 180  # 设置为3分钟
                    
                    while not (self._found_completion and self._found_room):
                        # 每次检查当前URL是否包含room_id
                        if not self._found_room:
                            self._check_url_for_room_id(self.page)
                            
                        # 每10秒尝试从Application获取cookies
                        if not self._found_cookies and timeout_counter % 10 == 0:
                            self._get_cookies_from_application()
                            
                        self.page.wait_for_timeout(1000)  # 每秒检查一次
                        timeout_counter += 1
                        
                        if timeout_counter % 10 == 0:
                            # 更新状态消息，指导用户操作
                            status_msg = f"已等待{timeout_counter}秒，"
                            missing_steps = []
                            
                            if not self._found_room:
                                missing_steps.append("第二步：打开聊天页面获取URL")
                                # 检查当前URL
                                self._check_url_for_room_id(self.page)
                                
                            if not self._found_completion:
                                missing_steps.append("第一步：发送消息触发API请求")
                                
                            if missing_steps:
                                status_msg += f"请完成：{', '.join(missing_steps)}"
                                self._update_status(status_msg)
                        
                        if timeout_counter >= max_timeout:
                            logger.warning("抓取超时")
                            self._update_status("抓取超时，请重试")
                            break
                    
                    # 在获取到所有必要信息后，等待3秒再获取最终的cookies
                    if self._found_completion and self._found_room:
                        logger.info("已获取到必要信息，等待3秒后获取最终cookies...")
                        self._update_status("已获取到必要信息，正在完成最终步骤...")
                        self._get_final_cookies()
                    
                    # 检查是否获取到了所有必要信息
                    missing = []
                    if not self._found_completion:
                        missing.append("completion接口信息")
                    if not self._found_room:
                        missing.append("room_id")
                    if not self.cookies:
                        missing.append("cookies")
                    
                    if missing:
                        logger.error(f"抓取未完成，缺少: {', '.join(missing)}")
                        self._update_status(f"抓取未完成，缺少: {', '.join(missing)}")
                        raise Exception(f"抓取超时，未能获取到所有必要信息，缺少: {', '.join(missing)}")
                        
                    # 收集所有信息
                    logger.info("抓取完成，收集信息")
                    self._update_status("抓取完成，正在收集信息...")
                    result = {
                        'device_id': self.device_id,
                        'tea_uuid': self.tea_uuid,
                        'web_id': self.web_id,
                        'cookies': self.cookies,
                        'x_flow_trace': self.x_flow_trace,
                        'room_id': self.room_id
                    }
                    
                    # 关闭浏览器
                    logger.info("关闭浏览器")
                    self._update_status("正在关闭浏览器...")
                    browser.close()
                    
                    logger.info("抓取成功")
                    self._update_status("抓取成功")
                    
                    # 提示用户需要重启应用
                    logger.info("配置已保存，需要重启应用以应用更改")
                    self._update_status("配置已保存，请重启应用以应用更改")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"抓取过程中出错: {str(e)}")
                    self._update_status(f"抓取过程中出错: {str(e)}")
                    browser.close()
                    raise Exception(f"抓取失败: {str(e)}")
        except Exception as e:
            logger.error(f"抓取失败: {str(e)}")
            self._update_status(f"抓取失败: {str(e)}")
            raise Exception(f"抓取失败: {str(e)}") 