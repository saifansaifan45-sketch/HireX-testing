from ..base_page import BasePage
from config.settings import settings

class RecruiterDashboardPage(BasePage):
    URL = f"{settings.RECRUITER_URL}/dashboard"

    def __init__(self, page):
        super().__init__(page)
        self.sidebar_brand = page.locator('text=HireX Demo Corp EMPLOYER PORTAL, text=EMPLOYER PORTAL').first
        self.nav_jobs = page.locator('a[href="/jobs"]').first
        self.nav_applicants = page.locator('a[href="/applicants"]').first
        self.nav_interviews = page.locator('a[href="/interviews"]').first
        self.nav_documents = page.locator('a[href="/documents"]').first
        self.nav_team = page.locator('a[href="/team"]').first
        self.nav_settings = page.locator('a[href="/settings"]').first

    def open(self):
        self.navigate(self.URL)

    def is_loaded(self) -> bool:
        return "/dashboard" in self.page.url
