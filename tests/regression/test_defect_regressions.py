"""
HireX Regression Test Suite for Identified Defects
Defects Covered:
- DF-HX-001: CWE-213 / OWASP API3 Sensitive Data Exposure on Public GET /jobs
- DF-HX-002: Unhandled HTTP 500 Server Crash on POST /interviewer/interviews/:id/feedback
- DF-HX-003: Unhandled HTTP 500 Server Crash on POST /recruiter/interviewers/invite with missing name
- DF-HX-004: Missing Confirmation Guard on Candidate Application Wizard Reset Draft
"""
import pytest
import json
from playwright.sync_api import APIRequestContext, Page, expect
from config.settings import Settings

SENSITIVE_COMPANY_FIELDS = [
    "apiKeyHash",
    "apiKeyPrefix",
    "smtpHost",
    "smtpUser",
    "smtpPassword",
    "digitalSignatureUrl",
]

SENSITIVE_RECRUITER_FIELDS = [
    "inviteToken",
    "inviteExpiry",
    "password",
    "passwordHash",
]


class TestDefectRegressions:
    """Regression test cases verifying fix status for discovered HireX defects."""

    def test_df_001_jobs_api_no_sensitive_fields_exposure(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-001:
        Public GET /jobs must NEVER serialize sensitive internal company or recruiter credentials.
        Target: https://api.dev.hire.zobay.in/jobs
        """
        response = api_request_context.get(f"{Settings.API_BASE_URL}/jobs")
        assert response.status == 200, f"Expected 200 OK from public /jobs, got {response.status}"
        
        data = response.json()
        jobs = data.get("jobs", []) if isinstance(data, dict) else data
        assert len(jobs) > 0, "Expected at least one job in public job listing"

        leaked_attributes = []
        for job in jobs:
            company = job.get("company", {})
            recruiter = job.get("recruiter", {})

            for field in SENSITIVE_COMPANY_FIELDS:
                if field in company and company[field] is not None:
                    leaked_attributes.append(f"company.{field}")

            for field in SENSITIVE_RECRUITER_FIELDS:
                if field in recruiter and recruiter[field] is not None:
                    leaked_attributes.append(f"recruiter.{field}")

        # If any sensitive attributes are exposed, fail test with exact leaked fields
        assert not leaked_attributes, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-001 active: Sensitive attributes leaked in public /jobs: "
            f"{set(leaked_attributes)}"
        )

    def test_df_002_interview_feedback_handles_unready_status_gracefully(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-002:
        POST /interviewer/interviews/:id/feedback must return a 400 Bad Request with a structured error message
        when the interview status does not permit feedback, NOT crash with HTTP 500 Internal Server Error.
        """
        # Step 1: Login as interviewer
        login_res = api_request_context.post(
            f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
            data=json.dumps({"email": Settings.INTERVIEWER_EMAIL, "password": Settings.INTERVIEWER_PASSWORD}),
            headers={"Content-Type": "application/json", "Origin": Settings.INTERVIEWER_URL}
        )
        assert login_res.status == 200, f"Interviewer login failed with status {login_res.status}"

        # Step 2: Fetch interviews to get an active interview id
        interviews_res = api_request_context.get(
            f"{Settings.API_BASE_URL}/interviewer/interviews",
            headers={"Origin": Settings.INTERVIEWER_URL}
        )
        assert interviews_res.status == 200
        interviews_data = interviews_res.json()
        interviews = interviews_data.get("interviews", []) if isinstance(interviews_data, dict) else interviews_data
        
        if not interviews:
            pytest.skip("No interviews assigned to interviewer test account to verify feedback endpoint")

        target_interview_id = interviews[0].get("id")

        # Step 3: Attempt feedback submission
        feedback_payload = {
            "ratings": {"technical": 4, "communication": 4},
            "recommendation": "HIRE",
            "notes": "Regression test probe"
        }
        feedback_res = api_request_context.post(
            f"{Settings.API_BASE_URL}/interviewer/interviews/{target_interview_id}/feedback",
            data=json.dumps(feedback_payload),
            headers={"Content-Type": "application/json", "Origin": Settings.INTERVIEWER_URL}
        )

        # The server must NOT crash with HTTP 500
        assert feedback_res.status != 500, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-002 active: POST /interviewer/interviews/{target_interview_id}/feedback "
            f"crashed with HTTP 500 Internal Server Error. Response: {feedback_res.text()}"
        )
        # Expected proper HTTP status is 200, 201 or 400 with validation message
        assert feedback_res.status in [200, 201, 400, 422], (
            f"Unexpected status {feedback_res.status} returned from feedback submission: {feedback_res.text()}"
        )

    def test_df_003_interviewer_invite_validates_missing_name(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-003:
        POST /recruiter/interviewers/invite must reject missing required 'name' field with 400 Bad Request,
        NOT crash with HTTP 500 Internal Server Error.
        """
        # Step 1: Login as recruiter
        login_res = api_request_context.post(
            f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
            data=json.dumps({"email": Settings.RECRUITER_EMAIL, "password": Settings.RECRUITER_PASSWORD}),
            headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
        )
        assert login_res.status == 200, f"Recruiter login failed with status {login_res.status}"

        # Step 2: Send invite payload omitting mandatory 'name'
        invalid_payload = {
            "email": "auto-missing-name-check@example.com"
            # 'name' is intentionally omitted
        }
        invite_res = api_request_context.post(
            f"{Settings.API_BASE_URL}/recruiter/interviewers/invite",
            data=json.dumps(invalid_payload),
            headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
        )

        # The server must NOT crash with HTTP 500
        assert invite_res.status != 500, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-003 active: POST /recruiter/interviewers/invite "
            f"crashed with HTTP 500 Internal Server Error when 'name' field was missing. Response: {invite_res.text()}"
        )
        # Expected proper validation error is 400 Bad Request
        assert invite_res.status == 400, (
            f"Expected 400 Bad Request for missing required field 'name', got {invite_res.status}: {invite_res.text()}"
        )

    def test_df_004_team_invite_invalid_role_enum_validation(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-004:
        POST /recruiter/team/invite must reject invalid role strings with 400 Bad Request,
        NOT crash with HTTP 500 Internal Server Error.
        """
        # Step 1: Login as recruiter
        login_res = api_request_context.post(
            f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
            data=json.dumps({"email": Settings.RECRUITER_EMAIL, "password": Settings.RECRUITER_PASSWORD}),
            headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
        )
        assert login_res.status == 200

        # Step 2: Send invite with invalid role
        invalid_role_payload = {
            "email": "auto-role-validation@example.com",
            "role": "INVALID_SUPER_USER"
        }
        res = api_request_context.post(
            f"{Settings.API_BASE_URL}/recruiter/team/invite",
            data=json.dumps(invalid_role_payload),
            headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
        )
        assert res.status != 500, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-004 active: POST /recruiter/team/invite crashed with "
            f"HTTP 500 Internal Server Error for invalid role 'INVALID_SUPER_USER'. Response: {res.text()}"
        )
        assert res.status == 400, f"Expected 400 Bad Request, got {res.status}: {res.text()}"

    def test_df_005_team_invite_email_format_validation(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-005:
        POST /recruiter/team/invite must validate email syntax and reject non-email strings with 400 Bad Request,
        NOT return 201 Created and generate active invite tokens.
        """
        import time
        # Step 1: Login as recruiter with retry for rate-limiting
        login_res = None
        for _ in range(3):
            login_res = api_request_context.post(
                f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
                data=json.dumps({"email": Settings.RECRUITER_EMAIL, "password": Settings.RECRUITER_PASSWORD}),
                headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
            )
            if login_res.status == 200:
                break
            time.sleep(2)
        assert login_res.status == 200, f"Recruiter login failed: {login_res.status}"

        # Step 2: Send invite with malformed non-email string
        malformed_email_payload = {
            "email": "malformed_email_without_at_or_domain",
            "role": "MEMBER"
        }
        res = api_request_context.post(
            f"{Settings.API_BASE_URL}/recruiter/team/invite",
            data=json.dumps(malformed_email_payload),
            headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
        )
        assert res.status != 201, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-005 active: POST /recruiter/team/invite accepted "
            f"malformed email string and returned 201 Created: {res.text()}"
        )
        assert res.status == 400, f"Expected 400 Bad Request, got {res.status}: {res.text()}"

    def test_df_006_resume_urls_no_localhost_hardcoding(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-006:
        Candidate application and resume endpoints must never return hardcoded 'localhost:3001' URLs in cloud environment.
        """
        import time
        # Step 1: Login as recruiter with retry for rate-limiting
        login_res = None
        for _ in range(3):
            login_res = api_request_context.post(
                f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
                data=json.dumps({"email": Settings.RECRUITER_EMAIL, "password": Settings.RECRUITER_PASSWORD}),
                headers={"Content-Type": "application/json", "Origin": Settings.RECRUITER_URL}
            )
            if login_res.status == 200:
                break
            time.sleep(2)
        assert login_res.status == 200

        # Step 2: Fetch applications
        apps_res = api_request_context.get(
            f"{Settings.API_BASE_URL}/recruiter/applications",
            headers={"Origin": Settings.RECRUITER_URL}
        )
        assert apps_res.status == 200
        apps_data = apps_res.json()
        apps = apps_data.get("applications", []) if isinstance(apps_data, dict) else apps_data
        assert len(apps) > 0, "No applications returned to check resume URLs"

        localhost_urls = []
        for app in apps:
            snapshot_url = app.get("resumeSnapshotUrl") or ""
            resume_url = app.get("resume", {}).get("fileUrl") or ""
            if "localhost" in snapshot_url.lower():
                localhost_urls.append(f"app[{app.get('id')}].resumeSnapshotUrl={snapshot_url}")
            if "localhost" in resume_url.lower():
                localhost_urls.append(f"app[{app.get('id')}].resume.fileUrl={resume_url}")

        assert not localhost_urls, (
            f"[DEFECT REGRESSION FAILURE] DF-HX-006 active: Resume files contain broken hardcoded localhost URLs in cloud environment: "
            f"{localhost_urls}"
        )

    def test_df_007_candidate_profile_name_min_length_validation(self, api_request_context: APIRequestContext):
        """
        Regression Test for DF-HX-007:
        PUT /candidate/me must reject empty name strings with 400 Bad Request, NOT accept 200 OK.
        """
        import time
        login_res = None
        for _ in range(3):
            login_res = api_request_context.post(
                f"{Settings.API_BASE_URL}/api/auth/sign-in/email",
                data=json.dumps({"email": Settings.CANDIDATE_EMAIL, "password": Settings.CANDIDATE_PASSWORD}),
                headers={"Content-Type": "application/json", "Origin": Settings.CANDIDATE_URL}
            )
            if login_res.status == 200:
                break
            time.sleep(2)
        assert login_res.status == 200

        # Attempt to wipe candidate name to empty string
        res = api_request_context.put(
            f"{Settings.API_BASE_URL}/candidate/me",
            data=json.dumps({"name": ""}),
            headers={"Content-Type": "application/json", "Origin": Settings.CANDIDATE_URL}
        )

        # Restore name immediately regardless of result
        api_request_context.put(
            f"{Settings.API_BASE_URL}/candidate/me",
            data=json.dumps({"name": "Rahul Verma"}),
            headers={"Content-Type": "application/json", "Origin": Settings.CANDIDATE_URL}
        )

        assert res.status != 200, (
            "[DEFECT REGRESSION FAILURE] DF-HX-007 active: PUT /candidate/me accepted empty name string ('') with 200 OK."
        )
        assert res.status == 400, f"Expected 400 Bad Request, got {res.status}"

    def test_fp_001_candidate_reset_draft_dialog_behavior(self, page: Page):
        """
        Verification Test for FP-HX-001 (Closed as False Positive / Designed Behavior):
        Verifies that clicking 'Reset draft' triggers the native browser window.confirm dialog
        ('Reset application draft? This will clear your unsaved changes and re-populate from your profile.')
        which guards against accidental candidate data loss.
        """
        dialog_appeared = []
        def handle_dialog(dialog):
            dialog_appeared.append(dialog.message)
            dialog.dismiss()
        page.on("dialog", handle_dialog)

        # 1. Login as candidate
        page.goto(f"{Settings.CANDIDATE_URL}/login")
        page.fill("#login-email", Settings.CANDIDATE_EMAIL)
        page.fill("#login-password", Settings.CANDIDATE_PASSWORD)
        page.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(3000)

        # 2. Go to apply wizard
        page.goto(f"{Settings.CANDIDATE_URL}/careers/{Settings.CAREER_SLUG}/jobs/job-fs-04/apply")
        page.wait_for_timeout(3000)

        # Click Continue on Step 1 (Resume)
        continue_btn = page.locator('button:has-text("Continue")')
        if continue_btn.count() > 0:
            continue_btn.click()
            page.wait_for_timeout(2000)

        # Click 'Reset draft'
        reset_btn = page.locator('button:has-text("Reset draft")')
        if reset_btn.count() == 0:
            pytest.skip("Reset draft button not found on application wizard")

        reset_btn.click()
        page.wait_for_timeout(1000)

        # Check whether modal or native browser dialog appeared
        modal_visible = page.locator("[role='dialog'], [role='alertdialog']").is_visible()
        dialog_or_modal_shown = bool(dialog_appeared) or modal_visible

        print(f"\n[DF-004 CHECK] dialog_appeared={dialog_appeared}, modal_visible={modal_visible}")

        assert dialog_or_modal_shown, (
            "[DEFECT REGRESSION FAILURE] DF-HX-004 active: 'Reset draft' wiped candidate form inputs "
            "immediately without any confirmation dialog or modal guard."
        )
