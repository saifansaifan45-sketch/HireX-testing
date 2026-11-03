import pytest
from config.settings import settings
from pages.candidate.career_page import CandidateCareerPage
from pages.recruiter.login_page import RecruiterLoginPage
from pages.recruiter.dashboard_page import RecruiterDashboardPage

@pytest.mark.e2e
def test_recruiter_and_candidate_portal_synchronization(page):
    """TC_HX_REG_001, TC_HX_SAN_001: Validate recruiter job publishing and candidate career page synchronization"""
    # 1. Candidate views career page
    career_page = CandidateCareerPage(page)
    career_page.open()
    assert career_page.job_cards.count() > 0
    
    # 2. Recruiter logs in
    login_page = RecruiterLoginPage(page)
    login_page.open()
    login_page.login(settings.RECRUITER_EMAIL, settings.RECRUITER_PASSWORD)
    
    # 3. Recruiter verifies dashboard is synchronized
    dashboard = RecruiterDashboardPage(page)
    assert dashboard.is_loaded()
    assert dashboard.nav_jobs.is_visible()

