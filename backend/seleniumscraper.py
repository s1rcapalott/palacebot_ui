import logging
import seleniumwire as sw
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

class SeleniumScraper():

    def __init__(self, url,mode,json_data, proxy_manager= None):
        self.url = url
        self.mode = mode
        self.json_data = json_data
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.browser = None
        self.retry = 0
        self.proxy = None
        self.headless = None
        self.page = None
        self.task_id = id(self)
        self.proxy_manager = proxy_manager
        self.setup_done = False
        #add a logger to this class 

    async def setup(self,group_name = 'default'):
        if self.proxy_manager:
            self.proxy = await self.proxy_manager.assign_proxy_to_task(group_name = group_name,task_id = self.task_id)
    
    
    async def cleanup(self):
        if self.proxy_manager:
            await self.proxy_manager.release_proxy_from_task(self.task_id)

    
    def headers(self):
        base_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.shoepalace.com/",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1"
    }

        if self.mode == "super_safe":
            import random
            user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0"
            ]
            base_headers["User-Agent"] = random.choice(user_agents)
        else:
        # Regular or fast mode: use a fixed modern user-agent
            base_headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
            )

        return base_headers

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
        headers = self.headers()
        for k, v in headers.items():
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
