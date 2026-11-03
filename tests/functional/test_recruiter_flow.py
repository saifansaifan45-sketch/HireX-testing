import pytest
from config.settings import settings
from pages.recruiter.login_page import RecruiterLoginPage
from pages.recruiter.dashboard_page import RecruiterDashboardPage

@pytest.mark.functional
def test_recruiter_dashboard_sections(page):
    """TC_HX_DASH_001, TC_HX_DASH_003: Verify recruiter dashboard navigation and sidebar links"""
    login_page = RecruiterLoginPage(page)
    login_page.open()
    login_page.login(settings.RECRUITER_EMAIL, settings.RECRUITER_PASSWORD)
    
    dashboard = RecruiterDashboardPage(page)
    assert dashboard.is_loaded()
    assert dashboard.nav_jobs.is_visible()
    assert dashboard.nav_applicants.is_visible()
    assert dashboard.nav_interviews.is_visible()
    assert dashboard.nav_team.is_visible()
    assert dashboard.nav_settings.is_visible()

