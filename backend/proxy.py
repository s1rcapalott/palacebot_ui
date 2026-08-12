import logging
import aiohttp
import asyncio
import json
import os
import random
import re
import time
from pathlib import Path
from .Validator import Validator

class Proxy_Manager:
    def __init__(self, proxy_file="proxy.json", task_map_file="task_map.json"):
        self.proxy_file = Path(proxy_file)
        self.task_map_file = Path(task_map_file) # FIXED: was missing
        self.proxylist = {"Groups": []}
        self.task_proxy_map = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers: # FIXED: prevent duplicate handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.validator = Validator()
        self._proxy_re = re.compile(r"^(?P<scheme>http|https|socks5)://(?:(?P<user>[^:@]+):(?P<pass>[^@]+)@)?(?P<ip>[^:]+):(?P<port>\d+)$")

    # --- internal saves without lock (call only when lock already held) ---
    def _save_proxies_nolock(self):
        try:
            with open(self.proxy_file, "w") as f:
                json.dump(self.proxylist, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save proxies: {e}")

    def _save_task_map_nolock(self):
        try:
            with open(self.task_map_file, "w") as f:
                json.dump(self.task_proxy_map, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save task map: {e}")

    async def save_proxies(self):
        async with self.lock:
            self._save_proxies_nolock()
            self.logger.info(f"Proxies saved successfully to '{self.proxy_file}'.")

    async def load_proxies(self):
        async with self.lock:
            if not self.proxy_file.exists():
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

    async def save_task_map(self):
        async with self.lock:
            self._save_task_map_nolock()
            self.logger.info("Task map saved.")

    async def load_task_map(self):
        if not self.task_map_file.exists():
            return
        async with self.lock:
            try:
                with open(self.task_map_file, "r") as f:
                    self.task_proxy_map = json.load(f)
                self.logger.info("Task map loaded.")
            except Exception as e:
                self.logger.error(f"Failed to load task map: {e}")

    # --- group management (kept both names for compat) ---
    async def create_group(self, group_name):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    self.logger.warning(f"Group '{group_name}' already exists.")
                    return False
            self.proxylist["Groups"].append({"group_name": group_name, "proxies": []})
            self._save_proxies_nolock()
        self.logger.info(f"Group '{group_name}' created.")
        return True

    # alias so old code using add_group still works
    add_group = create_group

    async def add_proxy(self, proxy_str, group_name):
        validated_proxy = self.validator.validate_proxy_format(proxy_str)
        if not validated_proxy:
            self.logger.error(f"Invalid proxy format: {proxy_str}")
            return False
        async with self.lock:
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
                        "last_used_timestamp": 0.0,
                        "stage_stats": {},
                        "tags": [],
                        "notes": ""
                    })
                    self._save_proxies_nolock()
                    self.logger.info(f"Added proxy '{proxy_str}' to group '{group_name}'.")
                    return True
        self.logger.error(f"Group '{group_name}' not found.")
        return False

    async def delete_group(self, group_name, fallback_group=None):
        # FIXED: removed print() debug, fixed deadlock on save_proxies/save_task_map
        async with self.lock:
            original_count = len(self.proxylist["Groups"])
            self.proxylist["Groups"] = [g for g in self.proxylist["Groups"] if g["group_name"] != group_name]
            if len(self.proxylist["Groups"]) == original_count:
                self.logger.warning(f"Group '{group_name}' not found.")
                return False
            self._save_proxies_nolock()
            # collect affected tasks while still holding lock
            affected = [tid for tid, p in self.task_proxy_map.items() if await self.get_proxy_group_nolock(p) == group_name]
            for tid in affected:
                self.task_proxy_map.pop(tid, None)
            self._save_task_map_nolock()
            self.logger.info(f"Group '{group_name}' deleted.")

        # reassign outside lock to avoid deadlock
        for task_id in affected:
            if fallback_group:
                reassigned = await self.assign_proxy_to_task(fallback_group, task_id)
                if reassigned:
                    self.logger.info(f"Reassigned task {task_id} to fallback proxy {reassigned} after deleting group '{group_name}'.")
                else:
                    self.logger.warning(f"Task {task_id} could not be reassigned after group '{group_name}' deletion.")
        return True

    async def rename_group(self, old_name, new_name):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == old_name:
                    if any(g["group_name"] == new_name for g in self.proxylist["Groups"]):
                        self.logger.warning(f"Group name '{new_name}' already exists.")
                        return False
                    group["group_name"] = new_name
                    self._save_proxies_nolock()
                    self.logger.info(f"Group renamed from '{old_name}' to '{new_name}'.")
                    return True
            self.logger.warning(f"Group '{old_name}' not found.")
            return False

    async def get_proxy_group(self, proxy_str):
        for group in self.proxylist["Groups"]:
            if any(p.get("proxy") == proxy_str for p in group["proxies"]):
                return group["group_name"]
        return None

    async def get_proxy_group_nolock(self, proxy_str):
        # helper for use inside lock
        for group in self.proxylist["Groups"]:
            if any(p.get("proxy") == proxy_str for p in group["proxies"]):
                return group["group_name"]
        return None
    
    async def migrate_group(self, from_group, to_group):
        async with self.lock:
            from_data = next((g for g in self.proxylist["Groups"] if g["group_name"] == from_group), None)
            to_data = next((g for g in self.proxylist["Groups"] if g["group_name"] == to_group), None)
            if not from_data:
                self.logger.warning(f"Source group '{from_group}' not found.")
                return False
            if not to_data:
                self.logger.warning(f"Target group '{to_group}' not found.")
                return False
            proxies_to_move = from_data["proxies"]
            from_data["proxies"] = []
            to_data["proxies"].extend(proxies_to_move)
            self._save_proxies_nolock()
            self.logger.info(f"Proxies migrated from '{from_group}' to '{to_group}'.")
            return True

    # --- assignment (merged both versions, deadlock fixed, fallback outside lock) ---
    async def assign_proxy_to_task(self, group_name, task_id, cooldown_seconds=2, fallback_group=None):
        result = None
        async with self.lock:
            group = next((g for g in self.proxylist["Groups"] if g["group_name"] == group_name), None)
            if not group:
                self.logger.error(f"Group '{group_name}' not found.")
            else:
                now = time.monotonic() # FIXED: was asyncio.get_event_loop().time()
                available = [
                    p for p in group["proxies"]
                    if not p.get("blacklisted")
                    and p.get("proxy")
                    and (now - p.get("last_used_timestamp", 0) >= cooldown_seconds)
                ]
                if available:
                    # weighted choice = healthier proxies picked more often, keeps your healthscore logic
                    weights = [max(1, p.get("healthscore", 0) + 1) for p in available]
                    selected = random.choices(available, weights=weights, k=1)[0]
                    proxy_str = selected["proxy"]
                    self.task_proxy_map[task_id] = proxy_str
                    # update stats inline without calling update_proxy_stats (avoids double-lock)
                    selected["last_used_timestamp"] = now
                    selected["usage_count"] = selected.get("usage_count", 0) + 1
                    selected["success_count"] = selected.get("success_count", 0) + 1
                    total = selected.get("success_count", 0) + selected.get("fail_count", 0)
                    selected["healthscore"] = int((selected["success_count"] / total) * 100) if total else 0
                    self._save_proxies_nolock()
                    self._save_task_map_nolock()
                    self.logger.info(f"Assigned proxy {proxy_str} to task {task_id}.")
                    result = proxy_str
        
        if result:
            return result
        if fallback_group:
            self.logger.warning(f"No available proxies in '{group_name}', trying fallback '{fallback_group}'")
            return await self.assign_proxy_to_task(fallback_group, task_id, cooldown_seconds)
        self.logger.warning(f"No available proxies in group '{group_name}'.")
        return None

    async def rotate_proxy(self, group_name, task_id, cooldown_seconds=2):
        """Assign a new proxy to a task if the current one failed."""
        await self.release_proxy_from_task(task_id)
        return await self.assign_proxy_to_task(group_name, task_id, cooldown_seconds)

    async def release_proxy_from_task(self, task_id):
        async with self.lock:
            if task_id in self.task_proxy_map:
                released = self.task_proxy_map.pop(task_id)
                self._save_task_map_nolock()
                self.logger.info(f"Released proxy {released} from task {task_id}")

    # --- stats (merged both versions, kept health_max + stage_stats compat) ---
    async def update_proxy_stats(self, proxy_str, group_name, status="success", auto_blacklist_threshold=3, health_max=100):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] != group_name:
                    continue
                for proxy in group["proxies"]:
                    if proxy.get("proxy") == proxy_str:
                        proxy.setdefault("stage_stats", {})
                        proxy["usage_count"] = proxy.get("usage_count", 0) + 1
                        proxy["last_used_timestamp"] = time.monotonic()
                        if status == "success":
                            proxy["success_count"] = proxy.get("success_count", 0) + 1
                        elif status == "fail":
                            proxy["fail_count"] = proxy.get("fail_count", 0) + 1
                            if proxy["fail_count"] >= auto_blacklist_threshold:
                                proxy["blacklisted"] = True
                                self.logger.warning(f"Proxy {proxy_str} blacklisted.")
                        total = proxy.get("success_count", 0) + proxy.get("fail_count", 0)
                        if total > 0:
                            proxy["healthscore"] = max(0, min(health_max, int((proxy.get("success_count", 0) / total) * 100)))
                        else:
                            proxy["healthscore"] = 0
                        self._save_proxies_nolock()
                        return True
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False

    def log_proxy_event(self, proxy_str, task_id, event, stage="general"):
        self.logger.info(f"[{stage.upper()}] Task {task_id} | Proxy {proxy_str} | Event: {event}")

    async def record_checkout_feedback(self, proxy_str, group_name, task_id, success=True):
        status = "success" if success else "fail"
        await self.update_proxy_stats(proxy_str, group_name, status=status)
        self.log_proxy_event(proxy_str, task_id, f"Checkout {'succeeded' if success else 'failed'}", stage="checkout")

    async def record_stage_feedback(self, proxy_str, group_name, stage, success=True):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    for proxy in group["proxies"]:
                        if proxy.get("proxy") == proxy_str:
                            proxy.setdefault("stage_stats", {}).setdefault(stage, []).append(success)
                            break
        await self.update_proxy_stats(proxy_str, group_name, status="success" if success else "fail")

    # --- ping / health (merged both _evaluate_single_proxy into one) ---
    async def ping(self, proxy_str):
        url_proxy = proxy_str if proxy_str.startswith("http") else f"http://{proxy_str}"
        try:
            async with aiohttp.ClientSession() as session:
                start = time.monotonic()
                # FIXED: was shoepalace.com (Cloudflare false fails) -> neutral endpoint
                async with session.get("https://httpbin.org/ip", proxy=url_proxy, timeout=aiohttp.ClientTimeout(total=10)):
                    return time.monotonic() - start
        except Exception as e:
            self.logger.debug(f"Ping failed for {url_proxy}: {e}")
            return None

    async def ping_proxy(self, proxy_string):
        """Ping a proxy and return results for GUI. Used by proxy_manager_page."""
        result = await self.ping(proxy_string)
        if result:
            return {"success": True, "ping": round(result * 1000, 2), "healthscore": 100}
        else:
            return {"success": False, "ping": None, "healthscore": 0}

    async def _evaluate_single_proxy(self, proxy, group_name, semaphore=None):
        if semaphore:
            async with semaphore:
                result = await self.ping(proxy["proxy"])
        else:
            result = await self.ping(proxy["proxy"])
        status = "success" if result is not None else "fail"
        await self.update_proxy_stats(proxy["proxy"], group_name, status=status)
        if result is not None:
            async with self.lock:
                proxy["last_checked_ping"] = result * 1000
                self._save_proxies_nolock()

    async def proxy_health_check(self, max_concurrent=10):
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        for group in self.proxylist["Groups"]:
            for proxy in group["proxies"]:
                if not proxy.get("blacklisted"):
                    tasks.append(self._evaluate_single_proxy(proxy, group["group_name"], semaphore))
        if tasks:
            await asyncio.gather(*tasks)

    async def controlled_ping_all(self, max_concurrent=10):
        await self.proxy_health_check(max_concurrent=max_concurrent)

    async def auto_health_monitor(self, interval_seconds=600):
        while True:
            await self.proxy_health_check()
            await asyncio.sleep(interval_seconds)

    # --- cleanup helpers ---
    async def erase_proxies(self, *to_remove):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                before = len(group["proxies"])
                group["proxies"] = [p for p in group["proxies"] if p["proxy"] not in to_remove]
                after = len(group["proxies"])
                if before != after:
                    self.logger.info(f"Removed {before - after} proxies from group '{group['group_name']}'.")
            self._save_proxies_nolock()

    async def cleanup_stale_proxies(self, min_fail_rate=0.8, min_usage=5):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                original_count = len(group["proxies"])
                group["proxies"] = [
                    p for p in group["proxies"]
                    if not (p.get("usage_count", 0) >= min_usage and p.get("fail_count", 0) / max(1, p.get("success_count", 0) + p.get("fail_count", 1)) >= min_fail_rate)
                ]
                removed = original_count - len(group["proxies"])
                if removed > 0:
                    self.logger.info(f"Removed {removed} stale proxies from group '{group['group_name']}'.")
            self._save_proxies_nolock()

    def get_proxy_dict(self, proxy_str, target="selenium"):
        m = self._proxy_re.match(proxy_str.strip())
        if not m:
            self.logger.error(f"Invalid proxy format: {proxy_str}")
            return None
        parts = m.groupdict()
        clean = f"{parts['scheme']}://"
        if parts.get("user") and parts.get("pass"):
            clean += f"{parts['user']}:{parts['pass']}@"
        clean += f"{parts['ip']}:{parts['port']}"
        if target == "selenium":
            return {"http": clean, "https": clean, "no_proxy": "localhost,127.0.0.1"}
        elif target == "pyppeteer":
            return {"args": [f"--proxy-server={clean}"], "auth": {"username": parts['user'], "password": parts['pass']} if parts.get("user") else None}
        elif target == "playwright":
            d = {"server": clean}
            if parts.get("user"): d["username"] = parts['user']
            if parts.get("pass"): d["password"] = parts['pass']
            return d
        self.logger.error(f"Unknown target '{target}'")
        return None

    def active_proxy_assignments(self):
        for task_id, proxy in self.task_proxy_map.items():
            self.logger.info(f"Task {task_id} is using proxy {proxy}")

    # --- tags / notes / suggestions (all kept) ---
    async def add_tag_to_proxy(self, proxy_str, group_name, tag):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    for proxy in group["proxies"]:
                        if proxy.get("proxy") == proxy_str:
                            tags = proxy.get("tags", [])
                            if tag not in tags:
                                tags.append(tag)
                                proxy["tags"] = tags
                                self._save_proxies_nolock()
                                self.logger.info(f"Added tag '{tag}' to proxy '{proxy_str}' in group '{group_name}'.")
                                return True
                            else:
                                self.logger.warning(f"Proxy '{proxy_str}' already has tag '{tag}'.")
                                return False
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False

    async def remove_tag_from_proxy(self, proxy_str, group_name, tag):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    for proxy in group["proxies"]:
                        if proxy.get("proxy") == proxy_str:
                            tags = proxy.get("tags", [])
                            if tag in tags:
                                tags.remove(tag)
                                proxy["tags"] = tags
                                self._save_proxies_nolock()
                                self.logger.info(f"Removed tag '{tag}' from proxy '{proxy_str}' in group '{group_name}'.")
                                return True
                            else:
                                self.logger.warning(f"Proxy '{proxy_str}' does not have tag '{tag}'.")
                                return False
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False
    
    async def add_note_to_proxy(self, proxy_str, group_name, note):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    for proxy in group["proxies"]:
                        if proxy.get("proxy") == proxy_str:
                            proxy["note"] = note
                            self._save_proxies_nolock()
                            self.logger.info(f"Added note to proxy '{proxy_str}' in group '{group_name}'.")
                            return True
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False
    
    async def remove_note_from_proxy(self, proxy_str, group_name):
        async with self.lock:
            for group in self.proxylist["Groups"]:
                if group["group_name"] == group_name:
                    for proxy in group["proxies"]:
                        if proxy.get("proxy") == proxy_str:
                            if "note" in proxy:
                                del proxy["note"]
                                self._save_proxies_nolock()
                                self.logger.info(f"Removed note from proxy '{proxy_str}' in group '{group_name}'.")
                                return True
                            else:
                                self.logger.warning(f"Proxy '{proxy_str}' has no note to remove.")
                                return False
        self.logger.error(f"Proxy '{proxy_str}' not found in group '{group_name}'.")
        return False
    
    def suggest_tags(self, proxy_data):
        suggestions = []
        healthscore = proxy_data.get("healthscore", 0)
        ping = proxy_data.get("last_checked_ping", 0)
        usage_count = proxy_data.get("usage_count", 0)
        if usage_count == 0:
            suggestions.append("untested proxy")
            return suggestions
        if usage_count > 4:
           if healthscore >= 80:
            if ping > 0 and ping < 1000:
                suggestions.append("High Performance")
            elif ping >= 1000 and ping < 2000:
                suggestions.append("Reliable")
            elif ping >= 2000:
                suggestions.append("Reliable but Slow")
            else:
                suggestions.append("High Performance")
           elif healthscore >= 50:
            suggestions.append("Medium Performance")
           else:
            suggestions.append("Low Performance")
        if ping > 0:
            if ping < 500:
                suggestions.append("fast")
            elif ping < 1000:
                suggestions.append("medium-speed")
            elif ping < 2000:
                suggestions.append("slow")
            elif ping >= 2000:
                suggestions.append("very-slow") 
        if usage_count > 100:
            suggestions.append("Frequently Used")
        elif usage_count > 50:
            suggestions.append("Moderately Used")
        else:
            suggestions.append("Rarely Used")
        return suggestions