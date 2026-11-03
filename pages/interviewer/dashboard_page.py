from ..base_page import BasePage
from config.settings import settings

class InterviewerDashboardPage(BasePage):
    URL = f"{settings.INTERVIEWER_URL}/dashboard"

    def __init__(self, page):
        super().__init__(page)
        self.sidebar_brand = page.locator('text=INTERVIEWER WORKSPACE').first
        self.nav_interviews = page.locator('a[href="/interviews"]').first
        self.nav_availability = page.locator('a[href*="availability"]').first
        self.nav_history = page.locator('a[href="/history"]').first
        self.nav_profile = page.locator('a[href="/profile"]').first

    def open(self):
        self.navigate(self.URL)

    def is_loaded(self) -> bool:
        return "/dashboard" in self.page.url
