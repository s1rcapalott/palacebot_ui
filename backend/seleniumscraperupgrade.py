import logging
from selenium import webdriver
import asyncio
import time
import re
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from .proxy import Proxy_Manager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import contextlib
import platform
import random

try:
    from seleniumwire import webdriver as sw
    _SELENIUMWIRE_AVAILABLE = True
except Exception:
    sw = None
    _SELENIUMWIRE_AVAILABLE = False

class _SessionProfile:
    def __init__(self, system: str):
        if system == "darwin":
            self.platform_str = '"macOS"'
            self.user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ]
        elif system == "windows":
            self.platform_str = '"Windows"'
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ]
        else:
            self.platform_str = '"Linux"'
            self.user_agents = [
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            ]

        self.user_agent = random.choice(self.user_agents)
        # FIXED: was hardcoded, now matches UA version dynamically
        ver = re.search(r'Chrome/(\d+)', self.user_agent).group(1) if re.search(r'Chrome/(\d+)', self.user_agent) else "127"
        self.sec_ch_ua = f'"Not)A;Brand";v="99", "Google Chrome";v="{ver}", "Chromium";v="{ver}"'
        self.sec_ch_ua_full = f'"Not)A;Brand";v="99.0.0.0", "Google Chrome";v="{ver}.0.0.0", "Chromium";v="{ver}.0.0.0"'
        
        self.accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        self.encoding = "gzip, deflate, br, zstd"
        self.language = "en-US,en;q=0.9"
        self.priority = "u=0, i"
        self.dnt = "1"

class _SPSelectors:
    JSON_LD = "script[type='application/ld+json']"
    PRODUCT_TITLE = "h1.product__title, h1.product-title, h1"
    AVAILABILITY_BADGE = ".product__availability, .product-availability, [data-availability]"
    SIZE_OPTIONS = (
        'input[name="Size"], '
        'button[data-value], '
        '.swatch--size label, '
        '[data-option-name="Size"] label'
    )
    ADD_TO_CART = 'button[name="add"], button.add-to-cart, [data-add-to-cart]'

class SeleniumScraper:
    def __init__(self, url: str, mode: str = "regular", json_data: dict | None = None,
                 proxy_manager: Proxy_Manager | None = None, headless: bool | None = True,
                 logger: logging.Logger | None = None):
        self.profile = _SessionProfile(platform.system().lower())
        self.url = url
        self._last_url = None
        self.mode = mode
        self.json_data = json_data or {}
        self.proxy_manager = proxy_manager
        self.cookies = {}
        self.session_cookies = None
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", datefmt="%m-%d %H:%M:%S"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        self.browser = None
        self.retry = 0
        self.proxy = None
        self.headless = headless
        self.page = None
        self.task_id = id(self)
        self._setup_done = False
        if self.mode != "fast" and not _SELENIUMWIRE_AVAILABLE:
            self.logger.warning("seleniumwire not installed; falling back to 'fast' mode.")
            self.mode = "fast"

    async def setup(self, group_name='default'):
        if self.proxy_manager:
            self.proxy = await self.proxy_manager.assign_proxy_to_task(
                group_name=group_name, task_id=self.task_id
            )
            if self.proxy:
                self.logger.info(f"[setup] Assigned proxy {self.proxy} to task {self.task_id}")
            else:
                self.logger.warning("[setup] No proxy assigned; continuing without proxy.")
    
    async def cleanup(self):
        br = self.browser
        self.browser = None
        if br:
            try:
                await asyncio.to_thread(br.quit)
                self.logger.info(f"[cleanup] Closed browser for task {self.task_id}")
            except Exception as e:
                self.logger.debug(f"[cleanup] Ignored driver quit error: {e}")
        if self.proxy_manager:
            try:
                await self.proxy_manager.release_proxy_from_task(task_id=self.task_id)
                self.logger.info(f"[cleanup] Released proxy for task {self.task_id}")
            except Exception as e:
                self.logger.warning(f"[cleanup] Failed to release proxy: {e}")
    
    def headers(self, referer: str | None = None, is_navigation: bool = True):
        p = self.profile
        h = {
            "Accept": p.accept,
            "Accept-Encoding": p.encoding,
            "Accept-Language": p.language,
            "User-Agent": p.user_agent,
            "Sec-Ch-Ua": p.sec_ch_ua,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": p.platform_str,
            "Sec-Ch-Ua-Full-Version": p.sec_ch_ua_full,
            "Sec-Ch-Ua-Platform-Version": '""',
            "Priority": p.priority,
            "DNT": p.dnt,
            "Upgrade-Insecure-Requests": "1" if is_navigation else "0",
            "Cache-Control": "max-age=0" if is_navigation else "no-cache",
            "Sec-Fetch-Mode": "navigate" if is_navigation else "no-cors",
            "Sec-Fetch-Dest": "document" if is_navigation else "empty",
            "Sec-Fetch-User": "?1" if is_navigation else "?0",
        }
        if referer:
            h["Referer"] = referer
            h["Sec-Fetch-Site"] = "same-origin"
        else:
            h["Sec-Fetch-Site"] = "none"
        return h

    def get_options(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"--user-agent={self.profile.user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-features=IsolatedOrigins,site-per-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--lang=en-US,en")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        if self.proxy:
            proxy_url = self.proxy if "://" in self.proxy else f"http://{self.proxy}"
            chrome_options.add_argument(f"--proxy-server={proxy_url}")
        return chrome_options

    def _stealth_inject(self, driver):
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // kill Klaviyo / Attentive / JustUno popups before they show
                Object.defineProperty(window, 'Klaviyo', {get: () => undefined, set: () => {}});
                window.klaviyo = undefined;
                // nuke any modal that tries to inject later
                const mo = new MutationObserver(() => {
                    document.querySelectorAll('[class*="klaviyo"], [class*="needsclick"], [role="dialog"], [class*="modal"], [id*="attentive"]').forEach(el=>{
                        if(el.offsetHeight > 100) el.style.display='none';
                    });
                });
                mo.observe(document.documentElement, {childList: true, subtree: true});
            """
            })
        except: pass

    # keep your existing webdriver fix below it
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
            })
        except: pass

    def interceptor(self, request):
        # BLOCK popup scripts before they load - no script, no modal
        if any(x in request.url.lower() for x in ['klaviyo', 'attentive', 'justuno', 'listrak', 'email-signup']):
            request.abort()
            return
        is_nav = getattr(request, "resource_type", "") in ("document", "main_frame", "")
        referer = self._last_url if (self._last_url and "shoepalace.com" in self._last_url) else None
        hdrs = self.headers(referer=referer, is_navigation=is_nav)
        for k, v in hdrs.items():
            if k in request.headers:
                del request.headers[k]
            request.headers[k] = v
        for bad in ["X-SeleniumWire", "Proxy-Connection"]:
            if bad in request.headers:
                del request.headers[bad]
    
    def get_browser(self):
        options = self.get_options()
        if self.mode == "fast":
            self.browser = webdriver.Chrome(options=options)
            self._stealth_inject(self.browser)
            self.logger.info("Using raw Selenium in 'fast' mode (stealth patched).")
        else:
            sw_options = {
                'request_storage_base_dir': '/tmp/seleniumwire',
                'addr': '127.0.0.1',
                'auto_config': False
            }
            self.browser = sw.Chrome(options=options, seleniumwire_options=sw_options)
            self._stealth_inject(self.browser)
            self.browser.request_interceptor = self.interceptor
            self.logger.info(f"Using SeleniumWire in '{self.mode}' mode.")
        try:
            self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except: pass
        return self.browser
        
    # FIXED: was def + asyncio.run() + time.sleep() = blocking + RuntimeError if called from async loop
    # Now is async def + await + asyncio.sleep()
    async def get_page(self, url=None, group_name="default", timeout=30, retries=3, actions=None):
        target_url = url if url else self.url
        if "?" in target_url and "variant" in target_url:
            target_url = target_url.split("?")[0]  # strip query params for initial load
            print(f"stripped variant query for initial load: {target_url}")
        self.retry = 0
        while self.retry < retries:
            try:
                if not self._setup_done:
                    await self.setup(group_name=group_name)  # FIXED: was asyncio.run(self.setup(...))
                    self._setup_done = True
                driver = await asyncio.to_thread(self.get_browser)
                await asyncio.to_thread(driver.set_page_load_timeout, timeout)
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await asyncio.to_thread(driver.get, target_url)
                self._last_url = target_url
                await asyncio.sleep(random.uniform(0.8,1.2))
                await asyncio.to_thread(self.dismiss_any_popup, driver)
                if actions:
                    for action in actions:
                        await asyncio.to_thread(self._do_action, driver, action)
                self.page = await asyncio.to_thread(lambda: driver.page_source)
                return self.page
            except Exception as e:
                self.logger.error(f"Error loading page: {e}")
                self.retry += 1
                try: await asyncio.to_thread(self.browser.quit)
                except: pass
                self.browser = None
                await asyncio.sleep(2 ** self.retry + random.uniform(0,1))
        return None
    
    def get_json(self):
        if not self.page:
            return {}
        try:
            soup_scripts = self.browser.find_elements(By.CSS_SELECTOR, _SPSelectors.JSON_LD)
            for s in soup_scripts:
                try:
                    data = json.loads(s.get_attribute("innerHTML"))
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        return data
                except: continue
        except: pass
        return self.json_data

    def get_cookies(self):
        # Kept for API compatibility - returns driver cookies if available
        if self.browser:
            try:
                return self.browser.get_cookies()
            except: pass
        return self.cookies

    def get_price(self):
        # Kept stub - implement as needed
        data = self.get_json()
        if data and "offers" in data:
            offers = data["offers"]
            if isinstance(offers, dict):
                return offers.get("price")
            elif isinstance(offers, list) and offers:
                return offers[0].get("price")
        return None

    def _do_action(self, driver, action, default_wait=10):
        action_type = action.get("type")
        selector = action.get("selector")
        value = action.get("value", "")
        post_wait = action.get("wait", 0)
        if not action_type or not selector:
            self.logger.warning(f"Malformed action skipped: {action}")
            return
        wait = WebDriverWait(driver, default_wait)
        elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(random.uniform(0.2, 0.6))
        if action_type == "click":
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            try:
                elem.click()
            except:
                driver.execute_script("arguments[0].click();", elem)
        elif action_type == "input":
            elem.clear()
            for c in value:
                elem.send_keys(c)
                time.sleep(random.uniform(0.04, 0.12))
        elif action_type == "wait_for":
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        else:
            self.logger.warning(f"Unknown action type '{action_type}'")
        if post_wait:
            time.sleep(post_wait + random.uniform(0, 0.5))

    def dismiss_any_popup(self, driver):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        import time

    # 1. Gift card X - your screenshot (bare ×, Klaviyo, Attentive)
        for xpath in [
        '//button[contains(text(),"×")]',
        '//button[text()="X"]',
        '//span[contains(text(),"×")]/parent::button',
        '//div[contains(@class,"close")]//button',
        '//div[@role="dialog"]//button',
        ]:
            try:
                for b in driver.find_elements(By.XPATH, xpath):
                    if b.is_displayed() and b.size['width'] > 10:
                        driver.execute_script("arguments[0].click();", b)
                        time.sleep(0.5)
                        break
            except: pass

    # 2. Cookie Accept/Decline (this already works for you)
        try:
            for b in driver.find_elements(By.XPATH, '//button[contains(text(),"Accept") or contains(text(),"Decline")]'):
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(0.3)
                    break
        except: pass

    # 3. ESC
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.2)
        except: pass

    # 4. Nuke anything still blocking - handles bot-only inject that X click missed
        try:
            driver.execute_script("""
        document.querySelectorAll('[class*="klaviyo"],[class*="needsclick"],[role="dialog"],[class*="modal"],[id*="attentive"],[class*="popup"]')
        .forEach(el=>{ if(getComputedStyle(el).position==='fixed' && el.offsetHeight>100) el.remove(); });
         // NEW: kill that bottom WOOPS teaser that blocks ADD TO CART
        document.querySelectorAll('[class*="teaser"], [class*="WOOPS"], [id*="teaser"], [class*="onsite"]')
        .forEach(el=> el.remove());
        document.body.style.overflow='auto';
        document.documentElement.style.overflow='auto';
        """)
        except: pass