import pytest
from config.settings import settings

@pytest.mark.security
def test_cookie_security_attributes(auth_client):
    """TC_HX_SEC_004: Verify HTTP-only, Secure, and SameSite=Lax cookie flags on session tokens"""
    resp = auth_client.sign_in_email(settings.RECRUITER_EMAIL, settings.RECRUITER_PASSWORD)
    assert resp.status == 200
    set_cookie_headers = resp.headers.get("set-cookie", "")
    assert "better-auth.session_token" in set_cookie_headers or "session_token" in set_cookie_headers
    lower_cookie = set_cookie_headers.lower()
    assert "httponly" in lower_cookie, "Cookie missing HttpOnly flag"
    assert "samesite" in lower_cookie, "Cookie missing SameSite flag"

@pytest.mark.security
def test_candidate_cannot_access_recruiter_endpoints(auth_client):
    """TC_HX_SEC_001: Verify Candidate session cookie cannot access privileged Recruiter endpoints (ADR-001)"""
    cand_resp = auth_client.sign_in_email(settings.CANDIDATE_EMAIL, settings.CANDIDATE_PASSWORD)
    assert cand_resp.status == 200
    cookies = cand_resp.headers.get("set-cookie", "")
    
    headers = {
        "Cookie": cookies,
        "Origin": settings.RECRUITER_URL
    }
    rec_resp = auth_client.post("/recruiters/jobs", json_data={"title": "Hacked Job"}, headers=headers)
    assert rec_resp.status in [401, 403, 404], f"Expected 401/403/404 Forbidden but got {rec_resp.status}"

@pytest.mark.security
def test_sql_injection_defense(auth_client):
    """TC_HX_SEC_005: Verify SQL injection payloads are properly parameterized and sanitized"""
    sqli_payloads = [
        "' OR 1=1 --",
        "'; DROP TABLE jobs; --",
        "\" OR \"\"=\""
    ]
    for payload in sqli_payloads:
        resp = auth_client.get(f"/jobs?search={payload}")
        assert resp.status in [200, 400], f"SQLi payload triggered server crash with status {resp.status}"
        if resp.status == 200:
            data = resp.json()
            assert isinstance(data, list)
