from ..base_page import BasePage
from config.settings import settings

class CandidateDashboardPage(BasePage):
    URL = f"{settings.CANDIDATE_URL}/dashboard"

    def __init__(self, page):
        super().__init__(page)
        self.nav_applications = page.locator('a[href="/applications"]').first
        self.nav_interviews = page.locator('a[href="/interviews"]').first
        self.nav_documents = page.locator('a[href="/candidate/documents"]').first
        self.nav_resume = page.locator('a[href="/candidate/resume"]').first
        self.nav_profile = page.locator('a[href="/candidate/profile"]').first

    def open(self):
        self.navigate(self.URL)

    def is_loaded(self) -> bool:
        return "/dashboard" in self.page.url
