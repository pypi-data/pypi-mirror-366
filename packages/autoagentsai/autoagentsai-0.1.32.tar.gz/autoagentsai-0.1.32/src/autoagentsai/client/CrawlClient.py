import json
import requests
from bs4 import BeautifulSoup
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from ..utils import extract_json
from ..client import ChatClient

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

T = TypeVar("T", bound=BaseModel)


class SiteConfig:
    """网站配置类，定义特定网站的处理策略"""
    
    def __init__(
        self,
        name: str,
        selectors: List[str] = None,
        wait_time: int = 3000,
        scroll_behavior: bool = False,
        custom_actions: List[Dict[str, Any]] = None
    ):
        self.name = name
        self.selectors = selectors or []  # 等待的CSS选择器
        self.wait_time = wait_time  # 额外等待时间(毫秒)
        self.scroll_behavior = scroll_behavior  # 是否需要滚动
        self.custom_actions = custom_actions or []  # 自定义操作


class CrawlClient:
    """Firecrawl Extract 复刻版 - 可配置网站策略版本"""

    def __init__(self, chat_client: ChatClient, use_playwright: bool = True):
        self.chat_client = chat_client
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.site_configs = self._init_default_configs()

    def _init_default_configs(self) -> Dict[str, SiteConfig]:
        """初始化默认的网站配置"""
        return {
            "github.com/trending": SiteConfig(
                name="GitHub Trending",
                selectors=['article[class*="Box-row"]'],
                wait_time=2000,
                scroll_behavior=False
            ),
            "airbnb": SiteConfig(
                name="Airbnb",
                wait_time=6000,
                scroll_behavior=True,
                custom_actions=[
                    {"action": "scroll", "params": {"direction": "bottom"}},
                    {"action": "wait", "params": {"time": 2000}},
                    {"action": "click_if_exists", "params": {"selectors": [
                        "button[data-testid='show-more-reviews']",
                        "[data-testid='more-reviews']", 
                        "button:has-text('Show more')",
                        "button:has-text('もっと見る')", 
                        "button:has-text('すべて見る')",
                        ".show-more-reviews",
                        "[class*='show-more']",
                        "[class*='load-more']"
                    ]}},
                    {"action": "wait", "params": {"time": 2000}},
                    {"action": "scroll", "params": {"direction": "bottom"}},
                    {"action": "wait", "params": {"time": 1500}},
                    {"action": "click_if_exists", "params": {"selectors": [
                        "button[data-testid='show-more-reviews']",
                        "[data-testid='more-reviews']", 
                        "button:has-text('Show more')",
                        "button:has-text('もっと見る')", 
                        "button:has-text('すべて見る')"
                    ]}},
                    {"action": "wait", "params": {"time": 1500}},
                    {"action": "scroll", "params": {"direction": "bottom"}},
                    {"action": "wait", "params": {"time": 2000}}
                ]
            ),
            "amazon": SiteConfig(
                name="Amazon",
                selectors=['[data-hook="review-body"]', '#cm_cr-dp_d_reviews_0'],
                wait_time=2000,
                scroll_behavior=True
            ),
            "booking.com": SiteConfig(
                name="Booking",
                selectors=['.c-review', '[data-testid="review-card"]', '[class*="review"]'],
                wait_time=3000,
                scroll_behavior=True,
                custom_actions=[
                    {"action": "wait", "params": {"time": 2000}},
                    {"action": "click_if_exists", "params": {"selectors": [
                        'a:has-text("Read all reviews")',
                        'button:has-text("Read all reviews")',
                        '[data-testid*="read-all"]',
                        '[data-testid*="show-all"]',
                        'a:has-text("すべてのレビューを読む")',
                        'a[href*="reviews"]',
                        '.read-all-reviews',
                        '[class*="read-all"]',
                        '[class*="show-all"]'
                    ]}},
                    {"action": "wait", "params": {"time": 3000}},
                    {"action": "scroll", "params": {"direction": "bottom"}},
                    {"action": "wait", "params": {"time": 2000}}
                ]
            ),
            "tripadvisor": SiteConfig(
                name="TripAdvisor", 
                selectors=['.review-container', '[data-test-target="reviews-tab"]'],
                wait_time=2000,
                scroll_behavior=True
            ),
            "trip.com": SiteConfig(
                name="Trip.com",
                selectors=[
                    '[class*="review"]', 
                    '[class*="comment"]',
                    '[data-testid*="review"]',
                    '.user-review',
                    '.review-item'
                ],
                wait_time=3000,
                scroll_behavior=True,
                custom_actions=[
                    {"action": "wait", "params": {"time": 2000}},
                    {"action": "click_if_exists", "params": {"selectors": [
                        'button:has-text("すべての口コミを表示")',
                        'button:has-text("Show all reviews")',
                        'a:has-text("すべての口コミを表示")',
                        'a:has-text("Show all reviews")',
                        '[data-testid*="show-all"]',
                        '[data-testid*="read-all"]',
                        '.show-all-reviews',
                        '[class*="show-all"]',
                        '[href*="review"]'
                    ]}},
                    {"action": "wait", "params": {"time": 3000}},
                    {"action": "scroll", "params": {"direction": "bottom"}},
                    {"action": "wait", "params": {"time": 2000}}
                ]
            )
        }

    def add_site_config(self, url_pattern: str, config: SiteConfig):
        """添加自定义网站配置"""
        self.site_configs[url_pattern] = config
        print(f"✅ 已添加网站配置: {config.name} ({url_pattern})")

    def _detect_site_config(self, url: str) -> Optional[SiteConfig]:
        """检测URL对应的网站配置"""
        url_lower = url.lower()
        for pattern, config in self.site_configs.items():
            if pattern.lower() in url_lower:
                return config
        return None

    def _execute_custom_actions(self, page, actions: List[Dict[str, Any]]):
        """执行自定义操作"""
        for action in actions:
            action_type = action.get("action")
            params = action.get("params", {})
            
            try:
                if action_type == "scroll":
                    direction = params.get("direction", "bottom")
                    if direction == "bottom":
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    elif direction == "top":
                        page.evaluate("window.scrollTo(0, 0)")
                    
                elif action_type == "wait":
                    wait_time = params.get("time", 1000)
                    page.wait_for_timeout(wait_time)
                    
                elif action_type == "click":
                    selector = params.get("selector")
                    if selector:
                        page.click(selector)
                        
                elif action_type == "click_if_exists":
                    selectors = params.get("selectors", [])
                    clicked = False
                    for selector in selectors:
                        try:
                            if page.is_visible(selector):
                                page.click(selector)
                                print(f"    ✅ 点击了元素: {selector}")
                                clicked = True
                                break
                        except:
                            continue
                    if not clicked:
                        print(f"    ⚠️ 未找到可点击的元素: {selectors}")
                        
                elif action_type == "type":
                    selector = params.get("selector")
                    text = params.get("text", "")
                    if selector:
                        page.type(selector, text)
                        
                print(f"  ✅ 执行自定义操作: {action_type}")
                
            except Exception as e:
                print(f"  ⚠️ 自定义操作失败 {action_type}: {e}")

    # ========== 内部工具 ==========
    def _fetch_html_with_playwright(self, url: str) -> str:
        """使用 Playwright 获取动态加载的页面内容"""
        with sync_playwright() as p:
            # 配置浏览器选项
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            page = browser.new_page()
            
            # 设置超时时间
            page.set_default_navigation_timeout(60000)  # 60秒
            page.set_default_timeout(30000)  # 30秒
            
            # 设置更真实的用户代理和其他头信息
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            })
            
            try:
                print(f"🌐 使用 Playwright 访问: {url}")
                
                # 检测网站配置
                site_config = self._detect_site_config(url)
                if site_config:
                    print(f"🎯 检测到网站: {site_config.name}")
                
                # 先尝试较宽松的等待策略
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    print(f"✅ DOM 加载完成，等待动态内容...")
                    
                    # 等待可能的动态内容加载
                    page.wait_for_timeout(3000)
                    
                    # 应用网站特定配置
                    if site_config:
                        # 等待特定选择器
                        selector_found = False
                        for selector in site_config.selectors:
                            try:
                                page.wait_for_selector(selector, timeout=15000)
                                print(f"✅ {site_config.name} 内容加载完成 (选择器: {selector})")
                                selector_found = True
                                break
                            except:
                                continue
                                
                        if not selector_found and site_config.selectors:
                            print(f"⚠️ 未检测到 {site_config.name} 特定内容，继续获取现有内容")
                        
                        # 额外等待时间
                        if site_config.wait_time > 0:
                            page.wait_for_timeout(site_config.wait_time)
                        
                        # 滚动行为
                        if site_config.scroll_behavior:
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            page.wait_for_timeout(2000)
                        
                        # 执行自定义操作
                        if site_config.custom_actions:
                            print(f"🔧 执行 {site_config.name} 自定义操作...")
                            self._execute_custom_actions(page, site_config.custom_actions)
                    
                    else:
                        # 通用策略：无特定配置时的默认行为
                        print(f"🔄 使用通用等待策略")
                        page.wait_for_timeout(5000)
                    
                except Exception as e:
                    print(f"⚠️ domcontentloaded 策略失败，尝试基本加载: {e}")
                    # 回退到最基本的加载策略
                    page.goto(url, wait_until="load", timeout=45000)
                    page.wait_for_timeout(2000)
                
                html = page.content()
                
                # 打印DOM内容用于调试
                print(f"\n{'='*80}")
                print(f"🌐 DOM内容调试信息")
                print(f"{'='*80}")
                print(f"📊 HTML总长度: {len(html)} 字符")
                print(f"📄 页面标题: {page.title()}")
                print(f"🔗 当前URL: {page.url}")
                
                # 打印部分DOM内容（前2000字符）
                print(f"\n🔍 DOM内容预览 (前2000字符):")
                print("-" * 60)
                print(html[:2000])
                print("-" * 60)
                
                # 检测特定元素
                review_selectors = [
                    '[data-review-id]',
                    '[class*="review"]', 
                    '[class*="comment"]',
                    '.review',
                    '.comment',
                    '[data-testid*="review"]',
                    '[id*="review"]'
                ]
                
                print(f"\n🔍 评论元素检测:")
                for selector in review_selectors:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"  ✅ {selector}: {count} 个元素")
                    else:
                        print(f"  ❌ {selector}: 0 个元素")
                
                return html
                
            finally:
                browser.close()

    def _fetch_html_with_requests(self, url: str) -> str:
        """使用 requests 获取静态页面内容（回退方案）"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试 {attempt + 1}/{max_retries}: 使用 requests 访问")
                resp = requests.get(url, headers=headers, timeout=30)  # 增加超时时间到30秒
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:  # 最后一次尝试失败
                    raise e
                print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
                import time
                time.sleep(2)  # 等待2秒后重试

    def _fetch_html(self, url: str) -> str:
        """获取HTML内容，优先使用 Playwright，失败时回退到 requests"""
        if self.use_playwright:
            try:
                return self._fetch_html_with_playwright(url)
            except Exception as e:
                print(f"⚠️ Playwright 失败，回退到 requests: {e}")
                return self._fetch_html_with_requests(url)
        else:
            print(f"🌐 使用 requests 访问: {url}")
            return self._fetch_html_with_requests(url)

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for s in soup(["script", "style"]):
            s.decompose()
        return soup.get_text(separator="\n", strip=True)

    def _extract_with_llm(self, text: str, schema: type[BaseModel], prompt: str) -> dict:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)

        # 将消息列表合并成一个字符串，传递更多文本以确保包含仓库信息
        text_to_send = text  # 传递全部文本
        combined_prompt = f"""You are an extractor that outputs only valid JSON.

Webpage text:
{text_to_send}

Schema:
{schema_json}

Extract data according to the schema. {prompt}"""

        print(f"🤖 发送给LLM的prompt长度: {len(combined_prompt)} 字符")
        print(f"📋 Schema: {schema.__name__}")
        print(f"🎯 提取提示: {prompt}")
        print(f"💬 LLM响应:")
        
        content = ""
        for event in self.chat_client.invoke(prompt=combined_prompt):
            if event['type'] == 'token':
                print(event['content'], end='', flush=True)
                content += event['content']

        content = extract_json(content)
        return content


    # ========== 公开方法 ==========
    def scrape_url(
        self,
        url: str,
        schema: Optional[Type[T]] = None,
        prompt: str = "",
        formats: List[str] = ["extract"],
        custom_config: Optional[SiteConfig] = None
    ):
        """
        爬取URL并提取结构化数据
        
        Args:
            url: 目标URL
            schema: 数据结构模型
            prompt: 提取提示
            formats: 返回格式
            custom_config: 自定义网站配置（可选）
        """
        print(f"🌐 正在爬取: {url}")
        print(f"🔧 爬取方法: {'Playwright' if self.use_playwright else 'Requests'}")
        
        # 如果提供了自定义配置，临时使用
        if custom_config:
            original_config = self.site_configs.get(url)
            self.site_configs[url] = custom_config
            print(f"🎛️ 使用自定义配置: {custom_config.name}")
        
        try:
            html = self._fetch_html(url)
            text = self._clean_html(html)
            
            print(f"📄 清理后的文本长度: {len(text)} 字符")
            print(f"📝 文本:\n{text}")

            results = {}
            if "html" in formats:
                results["html"] = html
            if "markdown" in formats:
                try:
                    from markdownify import markdownify
                    results["markdown"] = markdownify(html)
                except ImportError:
                    results["markdown"] = text
            if "extract" in formats and schema:
                print(f"🤖 开始LLM提取...")
                data = self._extract_with_llm(text, schema, prompt)
                print(f"✅ LLM提取完成，原始数据: {data}")
                results["extract"] = schema.model_validate(data)

            return results
            
        finally:
            # 恢复原始配置
            if custom_config:
                if original_config:
                    self.site_configs[url] = original_config
                else:
                    self.site_configs.pop(url, None)

    def list_site_configs(self):
        """列出所有已配置的网站"""
        print("📋 已配置的网站:")
        for pattern, config in self.site_configs.items():
            print(f"  🌐 {config.name}: {pattern}")
            print(f"    - 选择器: {config.selectors}")
            print(f"    - 等待时间: {config.wait_time}ms")
            print(f"    - 滚动行为: {config.scroll_behavior}")
            print(f"    - 自定义操作: {len(config.custom_actions)}个")
            print()
