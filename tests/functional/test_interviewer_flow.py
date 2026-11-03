import pytest
from config.settings import settings
from pages.interviewer.login_page import InterviewerLoginPage
from pages.interviewer.dashboard_page import InterviewerDashboardPage

@pytest.mark.functional
def test_interviewer_dashboard_sections(page):
    """TC_HX_AVAIL_001, TC_HX_FEED_005: Verify interviewer workspace navigation and availability link"""
    login_page = InterviewerLoginPage(page)
    login_page.open()
    login_page.login(settings.INTERVIEWER_EMAIL, settings.INTERVIEWER_PASSWORD)
    
    dashboard = InterviewerDashboardPage(page)
    assert dashboard.is_loaded()
    assert dashboard.nav_interviews.is_visible()
    assert dashboard.nav_availability.is_visible()

