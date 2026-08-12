import asyncio
import logging
import random
import platform
import re
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .proxy import Proxy_Manager

class _SessionProfile:
    def __init__(self, system: str):
        if system == "darwin":
            self.platform_str = '"macOS"'
            self.ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        elif system == "windows":
            self.platform_str = '"Windows"'
            self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        else:
            self.platform_str = '"Linux"'
            self.ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        ver = re.search(r'Chrome/(\d+)', self.ua).group(1)
        self.sec_ch_ua = f'"Not)A;Brand";v="99", "Chromium";v="{ver}", "Google Chrome";v="{ver}"'
        self.sec_ch_ua_full = f'"Not)A;Brand";v="99.0.0.0", "Chromium";v="{ver}.0.0.0", "Google Chrome";v="{ver}.0.0.0"'

class PlaywrightScraper:
    def __init__(self, url: str, mode: str = "regular", proxy_manager: Proxy_Manager | None = None, headless: bool = True, logger: logging.Logger | None = None):
        self.profile = _SessionProfile(platform.system().lower())
        self.url = url
        self.last_url: Optional[str] = None
        self.mode = mode
        self.proxy_manager = proxy_manager
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%m-%d %H:%M:%S %(message)s"))
            self.logger.addHandler(h)
            self.logger.setLevel(logging.INFO)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.proxy: Optional[str] = None
        self.headless = headless
        self.task_id = id(self)
        self._setup_done = False

    async def setup(self, group_name='default'):
        if self.proxy_manager:
            self.proxy = await self.proxy_manager.assign_proxy_to_task(group_name=group_name, task_id=self.task_id)
            if self.proxy: self.logger.info(f"[setup] Assigned proxy {self.proxy} to task {self.task_id}")

    async def cleanup(self):
        if self.page: 
            try: await self.page.close()
            except: pass
        if self.context:
            try: await self.context.close()
            except: pass
        if self.browser:
            try: await self.browser.close()
            except: pass
        if self.playwright:
            try: await self.playwright.stop()
            except: pass
        if self.proxy_manager:
            try: await self.proxy_manager.release_proxy_from_task(task_id=self.task_id)
            except: pass
        self.page = self.context = self.browser = None

    def _get_proxy_config(self):
        if not self.proxy: return None
        # playwright expects dict with server, username, password
        m = re.match(r'^(?P<scheme>https?://)?(?:(?P<user>[^:]+):(?P<pass>[^@]+)@)?(?P<host>[^:]+):(?P<port>\d+)$', self.proxy)
        if not m: return None
        d = m.groupdict()
        cfg = {"server": f"http://{d['host']}:{d['port']}"}
        if d.get("user"): cfg["username"] = d["user"]
        if d.get("pass"): cfg["password"] = d["pass"]
        return cfg

    async def get_page(self, url=None, group_name="default", timeout=30000, retries=3, actions=None):
        target_url = url if url else self.url
        for attempt in range(retries):
            try:
                if not self._setup_done:
                    await self.setup(group_name=group_name)
                    self._setup_done = True

                self.playwright = await async_playwright().start()
                proxy_cfg = self._get_proxy_config()
                
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-dev-shm-usage']
                )
                self.context = await self.browser.new_context(
                    user_agent=self.profile.ua,
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    extra_http_headers={
                        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Sec-Ch-Ua': self.profile.sec_ch_ua,
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': self.profile.platform_str,
                    },
                    proxy=proxy_cfg
                )
                # stealth init script
                await self.context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
                """)
                self.page = await self.context.new_page()
                await self.page.goto(target_url, wait_until='domcontentloaded', timeout=timeout)
                await asyncio.sleep(random.uniform(1.2, 2.8))
                self.last_url = self.page.url

                if actions:
                    for action in actions:
                        await self._do_action(self.page, action)
                
                content = await self.page.content()
                return content

            except Exception as e:
                self.logger.error(f"[get_page] Attempt {attempt+1}/{retries} failed: {e}")
                await self.cleanup()
                await asyncio.sleep(2 ** (attempt+1) + random.uniform(0,1))
        return None

    async def _do_action(self, page: Page, action: Dict[str, Any]):
        t, sel, val = action.get("type"), action.get("selector"), action.get("value","")
        post_wait = action.get("wait", 0)
        if not t or not sel: return
        try:
            await page.wait_for_selector(sel, state='visible', timeout=10000)
            if t == "click":
                await page.hover(sel)
                await asyncio.sleep(random.uniform(0.15, 0.4))
                await page.click(sel, delay=random.randint(30,90))
            elif t == "input":
                await page.focus(sel)
                await page.type(sel, val, delay=random.randint(45,120))
            elif t == "wait_for":
                await page.wait_for_selector(sel, state='visible')
            if post_wait: await asyncio.sleep(post_wait + random.uniform(0.2,0.6))
        except Exception as e:
            self.logger.warning(f"Action {t} on {sel} failed: {e}")