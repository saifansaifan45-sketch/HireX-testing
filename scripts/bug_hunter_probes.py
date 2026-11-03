import json
import httpx

API_BASE = "https://api.dev.hire.zobay.in"
CANDIDATE_URL = "https://dev.candidate.hire.zobay.in"
RECRUITER_URL = "https://dev.recruiter.hire.zobay.in"
INTERVIEWER_URL = "https://dev.interviewer.hire.zobay.in"

client = httpx.Client(timeout=15.0, verify=False)
findings = []

def log_probe(probe_id, title, result, defect_candidate=False, details=""):
    status_str = "[DEFECT DETECTED]" if defect_candidate else "[OK]"
    print(f"\n{status_str} [{probe_id}] {title}")
    print(f"Result: {result}")
    print(f"Details: {details}")
    findings.append({
        "probe_id": probe_id,
        "title": title,
        "result": result,
        "defect_candidate": defect_candidate,
        "details": details
    })

# Recruiter auth
r_rec = client.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "recruiter@hirex.dev", "password": "Password123!"})
rec_cookie = r_rec.headers.get("set-cookie", "")

# Candidate auth
r_cand = client.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "rahul@hirex.dev", "password": "Password123!"}, headers={"Origin": CANDIDATE_URL})
cand_cookie = r_cand.headers.get("set-cookie", "")

# Interviewer auth
r_int = client.post(f"{API_BASE}/auth/interviewer/login", json={"email": "rahul.sharma@hirex.dev", "password": "Password123!"})
int_cookie = r_int.headers.get("set-cookie", "")

print("=== AUTH TOKENS ACQUIRED ===")

# PROBE 1: Sensitive Data Exposure in Jobs API
r_jobs = client.get(f"{API_BASE}/jobs")
if r_jobs.status_code == 200:
    jobs = r_jobs.json()
    first_job = jobs[0] if jobs else {}
    recruiter_obj = first_job.get("recruiter", {})
    # Check if internal recruiter ID / company internals are exposed
    log_probe("PR-01", "Public /jobs Sensitive Data Exposure Check", f"Status {r_jobs.status_code}", 
              defect_candidate=False,
              details=f"Recruiter object keys in public response: {list(recruiter_obj.keys())}")

# PROBE 2: Unauthenticated Access to Internal Search
r_search = client.get(f"{API_BASE}/search?q=admin")
log_probe("PR-02", "Unauthenticated GET /search?q=admin Access", f"Status {r_search.status_code}",
          defect_candidate=(r_search.status_code == 200),
          details=f"Status: {r_search.status_code}, Response: {r_search.text[:200]}")

# PROBE 3: Malformed JSON Payload on Core Endpoints
r_malformed = client.post(f"{API_BASE}/api/auth/sign-in/email", content="{malformed_json: true,", headers={"Content-Type": "application/json", "Origin": CANDIDATE_URL})
log_probe("PR-03", "Malformed JSON Handling on Sign-In", f"Status {r_malformed.status_code}",
          defect_candidate=(r_malformed.status_code == 500),
          details=f"Status: {r_malformed.status_code}, Response: {r_malformed.text[:200]}")

# PROBE 4: Application Status Transition - Invalid Status
dummy_app_id = "00000000-0000-0000-0000-000000000000"
r_invalid_status = client.patch(f"{API_BASE}/applications/{dummy_app_id}/status", json={"status": "INVALID_STATE_XYZ"}, headers={"Cookie": rec_cookie, "Origin": RECRUITER_URL})
log_probe("PR-04", "PATCH /applications/:id/status with Invalid Enum Value", f"Status {r_invalid_status.status_code}",
          defect_candidate=(r_invalid_status.status_code == 500),
          details=f"Status: {r_invalid_status.status_code}, Response: {r_invalid_status.text[:200]}")

# PROBE 5: Application Status Transition - Revert to APPLIED Guard
r_revert_applied = client.patch(f"{API_BASE}/applications/{dummy_app_id}/status", json={"status": "APPLIED"}, headers={"Cookie": rec_cookie, "Origin": RECRUITER_URL})
log_probe("PR-05", "PATCH /applications/:id/status Revert to APPLIED (FR-010)", f"Status {r_revert_applied.status_code}",
          defect_candidate=(r_revert_applied.status_code == 500 or r_revert_applied.status_code == 200),
          details=f"Status: {r_revert_applied.status_code}, Response: {r_revert_applied.text[:200]}")

# PROBE 6: Candidate Privilege Escalation on /applications/:id/status
r_cand_patch = client.patch(f"{API_BASE}/applications/{dummy_app_id}/status", json={"status": "OFFER_STAGE"}, headers={"Cookie": cand_cookie, "Origin": CANDIDATE_URL})
log_probe("PR-06", "Candidate Privilege Escalation on /applications/:id/status", f"Status {r_cand_patch.status_code}",
          defect_candidate=(r_cand_patch.status_code in [200, 204]),
          details=f"Status: {r_cand_patch.status_code}, Response: {r_cand_patch.text[:200]}")

# PROBE 7: Public Guest Resume Upload with Missing File
r_guest_nofile = client.post(f"{API_BASE}/public/guest-resume", data={"name": "Attacker", "email": "test@test.com"})
log_probe("PR-07", "POST /public/guest-resume without Multipart File", f"Status {r_guest_nofile.status_code}",
          defect_candidate=(r_guest_nofile.status_code == 500),
          details=f"Status: {r_guest_nofile.status_code}, Response: {r_guest_nofile.text[:200]}")

# PROBE 8: Schedular Webhook Signature Validation (Fail-Closed check)
r_webhook_unsigned = client.post(f"{API_BASE}/webhooks/schedular", json={"event": "meeting.ended", "meetingId": "fake-123"})
log_probe("PR-08", "Unsigned Webhook Ingestion (NFR-003)", f"Status {r_webhook_unsigned.status_code}",
          defect_candidate=(r_webhook_unsigned.status_code == 200),
          details=f"Status: {r_webhook_unsigned.status_code}, Response: {r_webhook_unsigned.text[:200]}")

# PROBE 9: Schedular Webhook with Forged x-signature Header
r_webhook_forged = client.post(f"{API_BASE}/webhooks/schedular", json={"event": "meeting.ended", "meetingId": "fake-123"}, headers={"x-signature": "forged_sha256_hash_1234567890abcdef"})
log_probe("PR-09", "Forged Signature Webhook Ingestion", f"Status {r_webhook_forged.status_code}",
          defect_candidate=(r_webhook_forged.status_code == 200),
          details=f"Status: {r_webhook_forged.status_code}, Response: {r_webhook_forged.text[:200]}")

# PROBE 10: Candidate Slot Booking on Non-Existent Slot ID
r_book_fake = client.post(f"{API_BASE}/interviews/booking", json={"slotId": "non-existent-slot-uuid"}, headers={"Cookie": cand_cookie, "Origin": CANDIDATE_URL})
log_probe("PR-10", "POST /interviews/booking with Non-existent Slot ID", f"Status {r_book_fake.status_code}",
          defect_candidate=(r_book_fake.status_code == 500),
          details=f"Status: {r_book_fake.status_code}, Response: {r_book_fake.text[:200]}")

# PROBE 11: Interviewer Availability Negative Day of Week
r_avail_neg = client.post(f"{API_BASE}/interviews/availability", json={"dayOfWeek": -1, "startTime": "10:00", "endTime": "12:00", "timezone": "Asia/Kolkata", "isRecurring": True}, headers={"Cookie": int_cookie, "Origin": INTERVIEWER_URL})
log_probe("PR-11", "POST /interviews/availability with Negative dayOfWeek (-1)", f"Status {r_avail_neg.status_code}",
          defect_candidate=(r_avail_neg.status_code in [200, 201, 500]),
          details=f"Status: {r_avail_neg.status_code}, Response: {r_avail_neg.text[:200]}")

# PROBE 12: Interviewer Availability End Time Before Start Time
r_avail_backwards = client.post(f"{API_BASE}/interviews/availability", json={"dayOfWeek": 1, "startTime": "18:00", "endTime": "09:00", "timezone": "Asia/Kolkata", "isRecurring": True}, headers={"Cookie": int_cookie, "Origin": INTERVIEWER_URL})
log_probe("PR-12", "POST /interviews/availability End Time Before Start Time", f"Status {r_avail_backwards.status_code}",
          defect_candidate=(r_avail_backwards.status_code in [200, 201]),
          details=f"Status: {r_avail_backwards.status_code}, Response: {r_avail_backwards.text[:200]}")

# PROBE 13: Offer Acceptance on Stale / Non-existent Offer ID
r_offer_fake = client.post(f"{API_BASE}/candidate/offers/{dummy_app_id}/accept", json={"signature": "Hacker"}, headers={"Cookie": cand_cookie, "Origin": CANDIDATE_URL})
log_probe("PR-13", "POST /candidate/offers/:id/accept with Non-existent Offer", f"Status {r_offer_fake.status_code}",
          defect_candidate=(r_offer_fake.status_code == 500),
          details=f"Status: {r_offer_fake.status_code}, Response: {r_offer_fake.text[:200]}")

# PROBE 14: Document Rejection without Mandatory Reason
r_doc_reject_noreason = client.patch(f"{API_BASE}/recruiters/documents/{dummy_app_id}/reject", json={}, headers={"Cookie": rec_cookie, "Origin": RECRUITER_URL})
log_probe("PR-14", "PATCH /recruiters/documents/:id/reject without Reason (FR-019)", f"Status {r_doc_reject_noreason.status_code}",
          defect_candidate=(r_doc_reject_noreason.status_code in [200, 204]),
          details=f"Status: {r_doc_reject_noreason.status_code}, Response: {r_doc_reject_noreason.text[:200]}")

# PROBE 15: Create Job with Negative Salary / Boundary Values
r_job_neg_sal = client.post(f"{API_BASE}/recruiters/jobs", json={"title": "Test", "salary": -50000}, headers={"Cookie": rec_cookie, "Origin": RECRUITER_URL})
log_probe("PR-15", "POST /recruiters/jobs with Negative Salary", f"Status {r_job_neg_sal.status_code}",
          defect_candidate=(r_job_neg_sal.status_code in [200, 201]),
          details=f"Status: {r_job_neg_sal.status_code}, Response: {r_job_neg_sal.text[:200]}")

# PROBE 16: Check HTTP Methods on Immutable Routes (e.g. DELETE on /jobs)
r_job_delete = client.delete(f"{API_BASE}/jobs", headers={"Cookie": rec_cookie})
log_probe("PR-16", "DELETE /jobs (Unimplemented Method)", f"Status {r_job_delete.status_code}",
          defect_candidate=(r_job_delete.status_code == 500),
          details=f"Status: {r_job_delete.status_code}, Response: {r_job_delete.text[:200]}")

with open("bug_hunter_findings.json", "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2)

print("\nWrote bug_hunter_findings.json successfully!")
