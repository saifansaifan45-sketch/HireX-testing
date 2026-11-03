from ..base_page import BasePage
from config.settings import settings

class RecruiterLoginPage(BasePage):
    URL = f"{settings.RECRUITER_URL}/login"

    def __init__(self, page):
        super().__init__(page)
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.sign_in_button = page.locator('button:has-text("Sign In")')
        self.remember_me_checkbox = page.locator('input[type="checkbox"]')
        self.error_banner = page.locator('.text-red-500, [role="alert"], .text-destructive')

    def open(self):
        self.navigate(self.URL)

    def login(self, email: str, password: str, remember_me: bool = False):
        self.email_input.fill(email)
        self.password_input.fill(password)
        if remember_me:
            self.remember_me_checkbox.check()
        self.sign_in_button.click()
        self.page.wait_for_timeout(3000)

