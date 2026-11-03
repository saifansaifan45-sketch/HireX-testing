from ..base_page import BasePage
from config.settings import settings

class CandidateLoginPage(BasePage):
    URL = f"{settings.CANDIDATE_URL}/login"

    def __init__(self, page):
        super().__init__(page)
        self.email_input = page.locator("#login-email")
        self.password_input = page.locator("#login-password")
        self.sign_in_button = page.locator('button[type="submit"]').first
        self.signup_name = page.locator("#signup-name")
        self.signup_email = page.locator("#signup-email")
        self.signup_password = page.locator("#signup-password")

    def open(self):
        self.navigate(self.URL)

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()
        self.page.wait_for_timeout(3000)
