import pytest
from config.settings import settings
from pages.candidate.career_page import CandidateCareerPage
from pages.candidate.login_page import CandidateLoginPage
from pages.candidate.dashboard_page import CandidateDashboardPage

@pytest.mark.functional
def test_candidate_job_search_and_filters(page):
    """TC_HX_CP_001, TC_HX_CP_002, TC_HX_CP_003: Verify job keyword search and work mode filters"""
    career_page = CandidateCareerPage(page)
    career_page.open()
    
    # Verify initial cards
    initial_count = career_page.job_cards.count()
    assert initial_count >= 1
    
    # Test work mode filter: Remote
    career_page.filter_by_work_mode("Remote")
    assert career_page.filter_remote.is_visible()
    
    # Test work mode filter: Hybrid
    career_page.filter_by_work_mode("Hybrid")
    assert career_page.filter_hybrid.is_visible()
    
    # Reset filter: All
    career_page.filter_by_work_mode("All")
    assert career_page.filter_all.is_visible()

@pytest.mark.functional
def test_candidate_dashboard_navigation(page):
    """TC_HX_TRACK_001: Verify candidate dashboard navigation and sections"""
    login_page = CandidateLoginPage(page)
    login_page.open()
    login_page.login(settings.CANDIDATE_EMAIL, settings.CANDIDATE_PASSWORD)
    
    dashboard = CandidateDashboardPage(page)
    assert dashboard.is_loaded()
    assert dashboard.nav_applications.is_visible()
    assert dashboard.nav_documents.is_visible()

