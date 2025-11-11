import logging
from selenium import webdriver
import asyncio
import time
import re
import json
from selenium.webdriver.chrome.options import Options
from proxy import Proxy_Manager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import contextlib
import platform
import random

try:
    import seleniumwire as sw
    _SELENIUMWIRE_AVAILABLE = True
except Exception:
    _SELENIUMWIRE_AVAILABLE = False

class _SessionProfile:
    def __init__(self, system: str):
        if system == "darwin":               # macOS
            self.platform_str = '"macOS"'
            self.user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            ]
        elif system == "windows":
            self.platform_str = '"Windows"'
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            ]
        else:                                # Linux
            self.platform_str = '"Linux"'
            self.user_agents = [
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            ]

        import random
        self.user_agent = random.choice(self.user_agents)

        # Keep UA-CH aligned with your UA version (simple/static for now)
        self.sec_ch_ua = '"Chromium";v="142", "Google Chrome";v="142", "Not:A-Brand";v="99"'

        # Sticky, human-like defaults for this task
        self.accept   = ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                         "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
        self.encoding = "gzip, deflate, br, zstd"
        self.language = "en-US,en;q=0.9"
        self.priority = "u=0, i"
        self.dnt      = "1"

class SeleniumScraper:
    """
    Modes:
      - "fast": raw Selenium (no request interception)
      - "regular" / "super_safe": SeleniumWire, header interceptor, etc. (requires seleniumwire)
    """

    def __init__(
        self,
        url: str,
        mode: str = "regular",
        json_data: dict | None = None,
        proxy_manager: Proxy_Manager | None = None,
        headless: bool | None = True,
        logger: logging.Logger | None = None,
    ):
        self.profile = _SessionProfile(platform.system().lower())
        self.url = url
        self.last_url = None
        self.mode = mode
        self.json_data = json_data or {}
        self.proxy_manager = proxy_manager
        self.cookies = {}
        self.session_cookies = None

        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%m-%d %H:%M:%S"))
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
            self.logger.warning(
                "seleniumwire not installed; falling back to 'fast' mode."
            )
            self.mode = "fast"

        
        #add a logger to this class 

    async def setup(self,group_name = 'default'):
        if self.proxy_manager:
            self.proxy = await self.proxy_manager.assign_proxy_to_task(
                group_name=group_name, task_id=self.task_id
            )
            if self.proxy:
                self.logger.info(f"[setup] Assigned proxy {self.proxy} to task {self.task_id}")
            else:
                self.logger.warning("[setup] No proxy assigned; continuing without proxy.")
            
    
    
    async def cleanup(self):
        """
    Close the browser first (so it stops using the proxy),
    then release the proxy. Non-fatal on errors.
        """
    # 1) Kill browser without blocking the event loop
        br = self.browser
        self.browser = None  # ensure we don't reuse a dying handle
        if br:
            try:
                await asyncio.to_thread(br.quit)
                self.logger.info(f"[cleanup] Closed browser for task {self.task_id}")
            except Exception as e:
                # keep shutdown quiet; driver may already be gone
                self.logger.debug(f"[cleanup] Ignored driver quit error: {e}")
    # 2) Release proxy after browser is closed
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
             "Sec-CH-UA": p.sec_ch_ua,
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": p.platform_str,
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
        #Prepares and returns the headers required for making HTTP requests.
        #Returns A dictionary containing HTTP headers.
        


    def get_options(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if self.proxy:
            chrome_options.add_argument(f"--proxy-server={self.proxy}")

        return chrome_options
   
    def get_cookies(self):
        pass
    
    
            

    def interceptor(self, request):
        # Treat document/main_frame as a navigation
        is_nav = getattr(request, "resource_type", "") in ("document", "main_frame", "")
        referer = self._last_url if (self._last_url and self._last_url.startswith("https://www.shoepalace.com")) else None
        hdrs = self.headers(referer=referer, is_navigation=is_nav)
        for k, v in hdrs.items():
            request.headers[k] = v
    
    def get_browser(self):
        options = self.get_options()

        if self.mode == "fast":
            self.browser = webdriver.Chrome(
            options=options
            )
            self.logger.info("Using raw Selenium in 'fast' mode.")
        else:
            self.browser = sw.Chrome(
                options=options,
                seleniumwire_options={"request_storage_base_dir": "/tmp/seleniumwire"},
                keep_alive=True
            )
            self.logger.info(f"Using SeleniumWire in '{self.mode}' mode.")

        self.browser.request_interceptor = self.interceptor
        return self.browser
        
        ## This method initializes and returns a Selenium WebDriver instance based on the specified mode.i still have to flesh out the rest of the code and add proxy support
    def get_page(self, url=None, group_name="default", timeout=30, retries=3, actions=None):
        target_url = url if url else self.url
        self.retry = 0
        while self.retry < retries:
            try:
                if not self.setup_done:
                    asyncio.run(self.setup(group_name=group_name))
                    self.setup_done = True

                driver = self.get_browser()
                driver.set_page_load_timeout(timeout)
                driver.get(target_url)

                if actions:
                    for action in actions:
                        action_type = action.get("type")
                        selector = action.get("selector")
                        value = action.get("value", "")
                        wait_time = action.get("wait", 1)

                        if action_type == "click":
                            element = driver.find_element("css selector", selector)
                            element.click()
                        elif action_type == "input":
                            element = driver.find_element("css selector", selector)
                            element.clear()
                            element.send_keys(value)

                        time.sleep(wait_time)

                self.page = driver.page_source
                return self.page

            except Exception as e:
                self.logger.error(f"Error loading page: {e}")
                self.retry += 1
                time.sleep(2 ** self.retry)  # Exponential backoff
    
    def get_json(self):
        pass

    def get_price(self):
        driver = self.get_browser()
        driver.get(self.url)

    def _do_action(self, driver, action, default_wait=10):
        action_type = action.get("type")
        selector = action.get("selector")
        value = action.get("value", "")
        post_wait = action.get("wait", 0)

        if not action_type or not selector:
            self.logger.warning(f"Malformed action skipped: {action}")
            return

        wait = WebDriverWait(driver, default_wait)
        elem = asyncio.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

        if action_type == "click":
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elem.click()
        elif action_type == "input":
            elem.clear()
            elem.send_keys(value)
        elif action_type == "wait_for":
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        else:
            self.logger.warning(f"Unknown action type '{action_type}'")

        if post_wait:
            time.sleep(post_wait)

    
    
        
    #this function should grab the user data from the json file that is passed in the init function
