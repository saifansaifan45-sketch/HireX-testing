import pytest
from config.settings import settings

@pytest.mark.api
def test_get_jobs_schema(jobs_client):
    """TC_HX_API_001: Verify GET /jobs returns public jobs array with HTTP 200 and valid schema"""
    resp = jobs_client.get_public_jobs()
    assert resp.status == 200
    jobs = resp.json()
    assert isinstance(jobs, list)
    assert len(jobs) >= 1
    job = jobs[0]
    for key in ["id", "companyId", "title", "description", "location", "workMode", "employmentType", "status"]:
        assert key in job, f"Missing expected key {key} in job schema"

@pytest.mark.api
def test_get_single_job_details(jobs_client):
    """TC_HX_API_002: Verify GET /jobs/:id returns single job requisition details"""
    all_jobs = jobs_client.get_public_jobs().json()
    job_id = all_jobs[0]["id"]
    resp = jobs_client.get_job_by_id(job_id)
    assert resp.status == 200
    job = resp.json()
    assert job["id"] == job_id
    assert "company" in job
    assert "screeningQuestions" in job or "applicationForm" in job

@pytest.mark.api
def test_get_nonexistent_job_returns_404(jobs_client):
    """TC_HX_API_003: Verify GET /jobs/:id returns HTTP 404 on non-existent job ID"""
    dummy_id = "00000000-0000-0000-0000-000000000000"
    resp = jobs_client.get_job_by_id(dummy_id)
    assert resp.status == 404

@pytest.mark.api
def test_candidate_signin_api(auth_client):
    """TC_HX_AUTH_001: Verify candidate signup / signin establishing Better-Auth session"""
    resp = auth_client.sign_in_email(settings.CANDIDATE_EMAIL, settings.CANDIDATE_PASSWORD)
    assert resp.status == 200
    data = resp.json()
    assert data.get("user") is not None
    assert data["user"]["email"] == settings.CANDIDATE_EMAIL

@pytest.mark.api
def test_interviewer_login_api(auth_client):
    """TC_HX_AUTH_006: Verify interviewer login via specialized auth endpoint /auth/interviewer/login"""
    resp = auth_client.interviewer_login(settings.INTERVIEWER_EMAIL, settings.INTERVIEWER_PASSWORD)
    assert resp.status in [200, 201]
    data = resp.json()
    assert data.get("success") is True or "user" in data
    assert data["user"]["email"] == settings.INTERVIEWER_EMAIL
    assert data["user"]["role"] == "INTERVIEWER"

@pytest.mark.api
def test_recruiter_signin_invalid_password(auth_client):
    """TC_HX_AUTH_005: Verify error response when entering invalid credentials"""
    resp = auth_client.sign_in_email(settings.RECRUITER_EMAIL, "WrongPassword999!")
    assert resp.status in [400, 401, 403]

@pytest.mark.api
def test_global_search_api(auth_client):
    """TC_HX_API_006: Verify global search GET /search?q=test returns valid results"""
    resp = auth_client.get("/search?q=engineer")
    assert resp.status == 200
    data = resp.json()
    assert "results" in data or "query" in data

@pytest.mark.api
def test_aggregator_xml_feeds(auth_client):
    """TC_HX_API_007: Verify aggregator feeds GET /feeds/indeed-jobs.xml returns valid XML"""
    resp = auth_client.get("/feeds/indeed-jobs.xml")
    assert resp.status == 200
    content_type = resp.headers.get("content-type", "")
    assert "xml" in content_type or "text" in content_type

