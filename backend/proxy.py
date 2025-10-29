import logging
import aiohttp
import asyncio
import json
import os
import random
import re
from .Validator import Validator

class Proxy_Manager:
    def __init__(self, proxy_file="proxy.json"):
        self.proxy_file = proxy_file
        self.proxylist = {"Groups": []}
        self.task_proxy_map = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.validator = Validator()

    async def save_proxies(self):
        async with self.lock:
            try:
                with open(self.proxy_file, "w") as f:
                    json.dump(self.proxylist, f, indent=4)
                self.logger.info(f"Proxies saved successfully to '{self.proxy_file}'.")
            except Exception as e:
                self.logger.error(f"Failed to save proxies: {e}")

    async def load_proxies(self):
        async with self.lock:
            if not os.path.exists(self.proxy_file):
                self.logger.warning("Proxy file does not exist. Starting with empty list.")
                self.proxylist = {"Groups": []}
                return
            try:
                with open(self.proxy_file, "r") as f:
                    self.proxylist = json.load(f)
                self.logger.info("Proxies loaded successfully.")
            except Exception as e:
                self.logger.error(f"Failed to load proxies: {e}")
                self.proxylist = {"Groups": []}

    async def create_group(self, group_name):
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                self.logger.warning(f"Group '{group_name}' already exists.")
                return False
        self.proxylist["Groups"].append({"group_name": group_name, "proxies": []})
        await self.save_proxies()
        self.logger.info(f"Group '{group_name}' created.")
        return True

    async def add_proxy(self, proxy_str, group_name):
        validated_proxy = self.validator.validate_proxy_format(proxy_str)
        if not validated_proxy:
            self.logger.error(f"Invalid proxy format: {proxy_str}")
            return False
        
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                for proxy in group["proxies"]:
                    if proxy.get("proxy") == validated_proxy:
                        self.logger.warning(f"Proxy '{validated_proxy}' already exists in group '{group_name}'.")
                        return False
                group["proxies"].append({
                    "proxy": validated_proxy,
                    "last_checked_ping": 0,
                    "healthscore": 0,
                    "usage_count": 0,
                    "fail_count": 0,
                    "success_count": 0,
                    "blacklisted": False,
                    "last_used_timestamp": 0
                })
                await self.save_proxies()
                self.logger.info(f"Added proxy '{proxy_str}' to group '{group_name}'.")
                return True
        self.logger.error(f"Group '{group_name}' not found.")
        return False

    async def rotate_proxy(self, group_name, task_id, cooldown_seconds=2):
        """Assign a new proxy to a task if the current one failed."""
        await self.release_proxy_from_task(task_id)
        return await self.assign_proxy_to_task(group_name, task_id, cooldown_seconds)

    async def auto_health_monitor(self, interval_seconds=600):
        while True:
            await self.proxy_health_check()
            await asyncio.sleep(interval_seconds)

    async def _evaluate_single_proxy(self, proxy, group_name, semaphore=None):
        if semaphore:
            async with semaphore:
                result = await self.ping(proxy["proxy"])
        else:
            result = await self.ping(proxy["proxy"])
        status = "success" if result else "fail"
        await self.update_proxy_stats(proxy["proxy"], group_name, status=status)

    async def controlled_ping_all(self, max_concurrent=10):
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        for group in self.proxylist["Groups"]:
            for proxy in group["proxies"]:
                if proxy.get("blacklisted"):
                    continue
                tasks.append(self._evaluate_single_proxy(proxy, group["group_name"], semaphore))
        await asyncio.gather(*tasks)

    def log_proxy_event(self, proxy_str, task_id, event, stage="general"):
        self.logger.info(f"[{stage.upper()}] Task {task_id} | Proxy {proxy_str} | Event: {event}")

    async def record_checkout_feedback(self, proxy_str, group_name, task_id, success=True):
        status = "success" if success else "fail"
        await self.update_proxy_stats(proxy_str, group_name, status=status)
        self.log_proxy_event(proxy_str, task_id, f"Checkout {'succeeded' if success else 'failed'}", stage="checkout")

    async def assign_proxy_to_task(self, group_name, task_id, cooldown_seconds=2):
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                available = []
                for proxy in group["proxies"]:
                    if proxy.get("blacklisted"):
                        continue
                    if proxy.get("proxy") is None:
                        continue
                    if asyncio.get_event_loop().time() - proxy.get("last_used_timestamp", 0) < cooldown_seconds:
                        continue
                    available.append(proxy)
                if not available:
                    self.logger.warning(f"No available proxies in group '{group_name}'.")
                    return None
                selected = random.choice(available)
                proxy_str = selected["proxy"]
                self.task_proxy_map[task_id] = proxy_str
                await self.update_proxy_stats(proxy_str, group_name, status="success")
                self.logger.info(f"Assigned proxy {proxy_str} to task {task_id}.")
                return proxy_str
        self.logger.error(f"Group '{group_name}' not found.")
        return None

    async def update_proxy_stats(self, proxy_str, group_name, status="success", auto_blacklist_threshold=3, health_max=100):
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                for proxy in group["proxies"]:
                    if proxy.get("proxy") == proxy_str:
                        proxy["usage_count"] += 1
                        proxy["last_used_timestamp"] = asyncio.get_event_loop().time()
                        if status == "success":
                            proxy["success_count"] += 1
                        elif status == "fail":
                            proxy["fail_count"] += 1
                            if proxy["fail_count"] >= auto_blacklist_threshold:
                                proxy["blacklisted"] = True
                                self.logger.warning(f"Proxy {proxy_str} blacklisted.")
                        success = proxy.get("success_count", 1)
                        fail = proxy.get("fail_count", 0)
                        total = success + fail
                        proxy["healthscore"] = max(0, min(health_max, int((success / total) * 100)))
                        await self.save_proxies()
                        return True
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False

    async def ping(self, proxy_str):
        if not proxy_str.startswith("http"):
            proxy_str = f"http://{proxy_str}"
        try:
            async with aiohttp.ClientSession() as session:
                start = asyncio.get_event_loop().time()
                async with session.get("https://www.shoepalace.com", proxy=proxy_str, timeout=10):
                    end = asyncio.get_event_loop().time()
                    return end - start
        except Exception as e:
            self.logger.warning(f"Ping failed for {proxy_str}: {e}")
            return None

    async def proxy_health_check(self):
        tasks = []
        for group in self.proxylist["Groups"]:
            for proxy in group["proxies"]:
                if proxy.get("blacklisted"):
                    continue
                tasks.append(self._evaluate_single_proxy(proxy, group["group_name"]))
        await asyncio.gather(*tasks)

    async def _evaluate_single_proxy(self, proxy, group_name):
        result = await self.ping(proxy["proxy"])
        status = "success" if result else "fail"
        await self.update_proxy_stats(proxy["proxy"], group_name, status=status)

    async def erase_proxies(self, *to_remove):
        for group in self.proxylist["Groups"]:
            before = len(group["proxies"])
            group["proxies"] = [p for p in group["proxies"] if p["proxy"] not in to_remove]
            after = len(group["proxies"])
            if before != after:
                self.logger.info(f"Removed {before - after} proxies from group '{group['group_name']}'.")
        await self.save_proxies()

    async def release_proxy_from_task(self, task_id):
        if task_id in self.task_proxy_map:
            released = self.task_proxy_map.pop(task_id)
            self.logger.info(f"Released proxy {released} from task {task_id}")

    def get_proxy_dict(self, proxy_str, target="selenium"):
        pattern = re.compile(r"^(?P<scheme>http|https|socks5)://(?:(?P<user>[^:@]+):(?P<pass>[^@]+)@)?(?P<ip>[^:]+):(?P<port>\d+)$")
        match = pattern.match(proxy_str.strip())
        if not match:
            self.logger.error(f"Invalid proxy format: {proxy_str}")
            return None
        parts = match.groupdict()
        clean = f"{parts['scheme']}://"
        if parts.get("user") and parts.get("pass"):
            clean += f"{parts['user']}:{parts['pass']}@"
        clean += f"{parts['ip']}:{parts['port']}"
        if target == "selenium":
            return {"http": clean, "https": clean, "no_proxy": "localhost,127.0.0.1"}
        elif target == "pyppeteer":
            return {"args": [f"--proxy-server={clean}"], "auth": {"username": parts['user'], "password": parts['pass']} if parts.get("user") else None}
        self.logger.error(f"Unknown target '{target}'")
        return None

    def active_proxy_assignments(self):
        for task_id, proxy in self.task_proxy_map.items():
            self.logger.info(f"Task {task_id} is using proxy {proxy}")

    async def save_task_map(self):
        async with self.lock:
            try:
                with open(self.task_map_file, "w") as f:
                    json.dump(self.task_proxy_map, f, indent=4)
                self.logger.info("Task map saved.")
            except Exception as e:
                self.logger.error(f"Failed to save task map: {e}")

    async def load_task_map(self):
        if os.path.exists(self.task_map_file):
            async with self.lock:
                try:
                    with open(self.task_map_file, "r") as f:
                        self.task_proxy_map = json.load(f)
                    self.logger.info("Task map loaded.")
                except Exception as e:
                    self.logger.error(f"Failed to load task map: {e}")

    async def cleanup_stale_proxies(self, min_fail_rate=0.8, min_usage=5):
        for group in self.proxylist["Groups"]:
            original_count = len(group["proxies"])
            group["proxies"] = [
                p for p in group["proxies"]
                if not (p.get("usage_count", 0) >= min_usage and p.get("fail_count", 0) / max(1, p.get("success_count", 0) + p.get("fail_count", 1)) >= min_fail_rate)
            ]
            removed = original_count - len(group["proxies"])
            if removed > 0:
                self.logger.info(f"Removed {removed} stale proxies from group '{group['group_name']}'.")
        await self.save_proxies()

    async def assign_proxy_to_task(self, group_name, task_id, cooldown_seconds=2, fallback_group=None):
        def find_available(group):
            return [
                p for p in group["proxies"]
                if not p.get("blacklisted")
                and p.get("proxy")
                and asyncio.get_event_loop().time() - p.get("last_used_timestamp", 0) >= cooldown_seconds
            ]

        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                available = find_available(group)
                if not available and fallback_group:
                    self.logger.warning(f"No available proxies in '{group_name}', trying fallback '{fallback_group}'")
                    return await self.assign_proxy_to_task(fallback_group, task_id, cooldown_seconds)
                if not available:
                    self.logger.warning(f"No proxies available in group '{group_name}'.")
                    return None
                selected = random.choice(available)
                proxy_str = selected["proxy"]
                self.task_proxy_map[task_id] = proxy_str
                await self.update_proxy_stats(proxy_str, group_name, status="success")
                await self.save_task_map()
                self.logger.info(f"Assigned proxy {proxy_str} to task {task_id}.")
                return proxy_str
        self.logger.error(f"Group '{group_name}' not found.")
        return None

    async def update_proxy_stats(self, proxy_str, group_name, status="success", auto_blacklist_threshold=3, health_max=100):
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                for proxy in group["proxies"]:
                    if proxy.get("proxy") == proxy_str:
                        proxy.setdefault("stage_stats", {"page": [], "checkout": []})
                        proxy["usage_count"] += 1
                        proxy["last_used_timestamp"] = asyncio.get_event_loop().time()
                        if status == "success":
                            proxy["success_count"] += 1
                        elif status == "fail":
                            proxy["fail_count"] += 1
                            if proxy["fail_count"] >= auto_blacklist_threshold:
                                proxy["blacklisted"] = True
                                self.logger.warning(f"Proxy {proxy_str} blacklisted.")
                        success = proxy.get("success_count", 0)
                        fail = proxy.get("fail_count", 0)
                        total = success + fail
                        
                        if total >0:
                            proxy["healthscore"] = max(0, min(health_max, int((success / total) * 100)))
                        else:
                            proxy["healthscore"] = 0
                        await self.save_proxies()
                        return True
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False

    async def record_stage_feedback(self, proxy_str, group_name, stage, success=True):
        for group in self.proxylist["Groups"]:
            if group["group_name"] == group_name:
                for proxy in group["proxies"]:
                    if proxy.get("proxy") == proxy_str:
                        proxy.setdefault("stage_stats", {}).setdefault(stage, []).append(success)
                        await self.update_proxy_stats(proxy_str, group_name, status="success" if success else "fail")
                        return
        self.logger.warning(f"Could not record stage feedback for {proxy_str} in group {group_name}.")

    async def add_group(self, group_name):
        async with self.lock:
            if any(group["group_name"] == group_name for group in self.proxylist["Groups"]):
                self.logger.warning(f"Group '{group_name}' already exists.")
                return False
            self.proxylist["Groups"].append({"group_name": group_name, "proxies": []})
            await self.save_proxies()
            self.logger.info(f"Group '{group_name}' created.")
            return True

    async def delete_group(self, group_name, fallback_group=None):
        print(f"Entering delete_group with: {group_name}")
        async with self.lock:
            print("Lock acquired in delete_group")
            original_count = len(self.proxylist["Groups"])
            print(f"Original count: {original_count}")
            print(f"New count: {len(self.proxylist['Groups'])}")
            self.proxylist["Groups"] = [g for g in self.proxylist["Groups"] if g["group_name"] != group_name]
            print("Updated proxylist groups:", self.proxylist["Groups"])
            if len(self.proxylist["Groups"]) < original_count:
                await self.save_proxies()
                affected_tasks = []
                for tid, proxy in self.task_proxy_map.items():
                    group = await self.get_proxy_group(proxy)
                    if group == group_name:
                        affected_tasks.append(tid)
                for task_id in affected_tasks:
                    await self.release_proxy_from_task(task_id)
                    reassigned = None
                    if fallback_group:
                        reassigned = await self.assign_proxy_to_task(fallback_group, task_id)
                    if reassigned:
                        self.logger.info(f"Reassigned task {task_id} to fallback proxy {reassigned} after deleting group '{group_name}'.")
                    else:
                        self.logger.warning(f"Task {task_id} could not be reassigned after group '{group_name}' deletion.")
                await self.save_task_map()
                self.logger.info(f"Group '{group_name}' deleted.")
                return True
            self.logger.warning(f"Group '{group_name}' not found.")
            return False


    async def rename_group(self, old_name, new_name):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == old_name:
                    if any(g["group_name"] == new_name for g in self.proxylist["Groups"]):
                        self.logger.warning(f"Group name '{new_name}' already exists.")
                        return False
                    group["group_name"] = new_name
                    await self.save_proxies()
                    self.logger.info(f"Group renamed from '{old_name}' to '{new_name}'.")
                    return True
            self.logger.warning(f"Group '{old_name}' not found.")
            return False

    async def get_proxy_group(self, proxy_str):
        for group in self.proxylist["Groups"]:
            if any(p.get("proxy") == proxy_str for p in group["proxies"]):
                return group["group_name"]
        return None
    
    async def migrate_group(self, from_group, to_group):
        async with self.lock:
            from_group_data = None
            to_group_data = None

            for group in self.proxylist["Groups"]:
                if group["group_name"] == from_group:
                    from_group_data = group
                elif group["group_name"] == to_group:
                    to_group_data = group

            if not from_group_data:
                self.logger.warning(f"Source group '{from_group}' not found.")
                return False
            if not to_group_data:
                self.logger.warning(f"Target group '{to_group}' not found.")
                return False

        # Move proxies and clear source
            proxies_to_move = from_group_data["proxies"]
            from_group_data["proxies"] = []
            to_group_data["proxies"].extend(proxies_to_move)

            await self.save_proxies()
            self.logger.info(f"Proxies migrated from '{from_group}' to '{to_group}'.")
            return True
        
    async def ping_proxy(self, proxy_string):
        """Ping a proxy and return results for GUI. Used by proxy_manager_page."""
        result = await self.ping(proxy_string)
        if result:
            return {
                "success": True,
                "ping": round(result * 1000, 2),  # Convert seconds to milliseconds
                "healthscore": 100  # New proxy, assume healthy
            }
        else:
            return {
                "success": False,
                "ping": None,
                "healthscore": 0
            }


    
