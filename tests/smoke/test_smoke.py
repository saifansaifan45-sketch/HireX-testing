import pytest
from config.settings import settings
from pages.recruiter.login_page import RecruiterLoginPage
from pages.recruiter.dashboard_page import RecruiterDashboardPage
from pages.interviewer.login_page import InterviewerLoginPage
from pages.interviewer.dashboard_page import InterviewerDashboardPage
from pages.candidate.career_page import CandidateCareerPage
from pages.candidate.login_page import CandidateLoginPage
from pages.candidate.dashboard_page import CandidateDashboardPage

@pytest.mark.smoke
def test_recruiter_portal_loads(page):
    """TC_HX_SMK_001: Verify Recruiter Portal login page loads and responds with HTTP 200"""
    login_page = RecruiterLoginPage(page)
    login_page.open()
    assert "Recruiter Portal" in login_page.get_title() or "HireX Employer" in login_page.get_title()
    assert login_page.email_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.sign_in_button.is_visible()

@pytest.mark.smoke
def test_interviewer_portal_loads(page):
    """TC_HX_SMK_002: Verify Interviewer Portal login page loads and responds with HTTP 200"""
    login_page = InterviewerLoginPage(page)
    login_page.open()
    assert "Interviewer Portal" in login_page.get_title() or "HireX" in login_page.get_title()
    assert login_page.email_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.sign_in_button.is_visible()

@pytest.mark.smoke
def test_candidate_career_page_loads(page):
    """TC_HX_SMK_003: Verify Candidate Career Page loads and responds with HTTP 200"""
    career_page = CandidateCareerPage(page)
    career_page.open()
    assert "Careers" in career_page.get_title() or "Opportunities" in career_page.get_title()
    assert career_page.search_input.is_visible()
    assert career_page.filter_all.is_visible()

@pytest.mark.smoke
def test_backend_api_health_check(auth_client):
    """TC_HX_SMK_004: Verify Backend API health check endpoint returns status: ok"""
    resp = auth_client.get("/")
    assert resp.status == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "hirex-backend"

@pytest.mark.smoke
def test_public_jobs_endpoint(jobs_client):
    """TC_HX_SMK_005: Verify public jobs API endpoint returns active job requisitions"""
    resp = jobs_client.get_public_jobs()
    assert resp.status == 200
    jobs = resp.json()
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    assert "id" in jobs[0]
    assert "title" in jobs[0]

@pytest.mark.smoke
def test_recruiter_login_dashboard_access(page):
    """TC_HX_SMK_006: Verify Recruiter Admin can authenticate and land on /dashboard"""
    login_page = RecruiterLoginPage(page)
    login_page.open()
    login_page.login(settings.RECRUITER_EMAIL, settings.RECRUITER_PASSWORD)
    dashboard_page = RecruiterDashboardPage(page)
    assert dashboard_page.is_loaded()
    assert dashboard_page.nav_jobs.is_visible() or dashboard_page.nav_applicants.is_visible()

@pytest.mark.smoke
def test_interviewer_login_dashboard_access(page):
    """TC_HX_SMK_007: Verify Interviewer can authenticate and land on /dashboard"""
    login_page = InterviewerLoginPage(page)
    login_page.open()
    login_page.login(settings.INTERVIEWER_EMAIL, settings.INTERVIEWER_PASSWORD)
    dashboard_page = InterviewerDashboardPage(page)
    assert dashboard_page.is_loaded()

@pytest.mark.smoke
def test_candidate_login_dashboard_access(page):
    """TC_HX_SMK_008: Verify Candidate can authenticate and land on /dashboard"""
    login_page = CandidateLoginPage(page)
    login_page.open()
    login_page.login(settings.CANDIDATE_EMAIL, settings.CANDIDATE_PASSWORD)
    dashboard_page = CandidateDashboardPage(page)
    assert dashboard_page.is_loaded()

