import time
from playwright.sync_api import Page, Locator
from typing import Optional

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str, retries: int = 2):
        for attempt in range(retries + 1):
            try:
                self.page.goto(url, wait_until="load", timeout=30000)
                return
            except Exception as e:
                if attempt == retries:
                    raise
                time.sleep(2)

    def get_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    def wait_for_timeout(self, timeout_ms: float):
        self.page.wait_for_timeout(timeout_ms)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: float = 10000) -> Locator:
        return self.page.wait_for_selector(selector, state=state, timeout=timeout)
