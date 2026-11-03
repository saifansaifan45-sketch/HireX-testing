from ..base_page import BasePage
from config.settings import settings

class CandidateCareerPage(BasePage):
    URL = f"{settings.CANDIDATE_URL}/careers/{settings.CAREER_SLUG}"

    def __init__(self, page):
        super().__init__(page)
        self.search_input = page.locator('input[placeholder*="Search by role"]').first
        self.filter_all = page.locator('button:has-text("All")').first
        self.filter_remote = page.locator('button:has-text("Remote")').first
        self.filter_hybrid = page.locator('button:has-text("Hybrid")').first
        self.filter_onsite = page.locator('button:has-text("On-site")').first
        self.job_cards = page.locator('button:has-text("Developer"), button:has-text("Engineer"), div[class*="job-card"]')

    def open(self):
        self.navigate(self.URL)
        self.page.wait_for_timeout(2000)

    def search_jobs(self, query: str):
        self.search_input.fill(query)
        self.page.wait_for_timeout(1000)

    def filter_by_work_mode(self, mode: str):
        if mode.lower() == "remote":
            self.filter_remote.click()
        elif mode.lower() == "hybrid":
            self.filter_hybrid.click()
        elif mode.lower() == "on-site":
            self.filter_onsite.click()
        else:
            self.filter_all.click()
        self.page.wait_for_timeout(1000)
