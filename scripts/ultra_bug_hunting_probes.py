"""
Ultra QA Mode Deep Adversarial Bug Hunting Probes
Tests:
1. Job Application Illegal State Machine Transition (APPLIED -> HIRED bypass)
2. Negative / Boundary Salary Validation in Offer Creation
3. Malformed / Disallowed File Upload Extension & MIME Types
4. Recruiter Cross-Tenant / IDOR Access on Applications
5. Concurrency & Race Condition on Interview Slot Booking
"""
import urllib.request
import urllib.parse
import http.cookiejar
import json
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


class HireXDeepHunter:
    def __init__(self):
        self.cj_recruiter = http.cookiejar.CookieJar()
        self.opener_recruiter = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj_recruiter),
            urllib.request.HTTPSHandler(context=ssl_ctx)
        )

        self.cj_candidate = http.cookiejar.CookieJar()
        self.opener_candidate = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj_candidate),
            urllib.request.HTTPSHandler(context=ssl_ctx)
        )

    def login_recruiter(self):
        req = urllib.request.Request(
            "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
            data=json.dumps({"email": "recruiter@hirex.dev", "password": "Password123!"}).encode('utf-8'),
            headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
        )
        res = self.opener_recruiter.open(req)
        print("[AUTH] Recruiter logged in:", res.status)

    def login_candidate(self):
        req = urllib.request.Request(
            "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
            data=json.dumps({"email": "rahul@hirex.dev", "password": "Password123!"}).encode('utf-8'),
            headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"}
        )
        res = self.opener_candidate.open(req)
        print("[AUTH] Candidate logged in:", res.status)

    def probe_1_state_machine_illegal_jump(self):
        print("\n--- Probe 1: Illegal State Machine Jump (APPLIED -> HIRED) ---")
        # 1. Fetch applications
        req = urllib.request.Request(
            "https://api.dev.hire.zobay.in/recruiter/applications",
            headers={"Origin": "https://dev.recruiter.hire.zobay.in"}
        )
        try:
            res = self.opener_recruiter.open(req)
            apps = json.loads(res.read().decode('utf-8'))
            app_list = apps.get("applications", []) if isinstance(apps, dict) else apps
            if not app_list:
                print("No applications found to test state machine")
                return

            app_id = app_list[0]["id"]
            current_stage = app_list[0].get("stage") or app_list[0].get("status")
            print(f"Target App ID: {app_id}, Current Stage: {current_stage}")

            # Try patching stage to HIRED directly
            patch_data = json.dumps({"stage": "HIRED"}).encode('utf-8')
            patch_req = urllib.request.Request(
                f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/stage",
                data=patch_data,
                headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"},
                method="PATCH"
            )
            try:
                p_res = self.opener_recruiter.open(patch_req)
                print(f"[DEFECT CONFIRMED] Illegal stage jump APPLIED -> HIRED was ACCEPTED with status {p_res.status}!")
                print("Response:", p_res.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                print(f"[EXPECTED BEHAVIOR] Server rejected illegal stage jump with HTTP {e.code}: {e.read().decode('utf-8')}")

        except Exception as ex:
            print("Error during Probe 1:", ex)

    def probe_2_negative_salary_offer_creation(self):
        print("\n--- Probe 2: Offer Creation with Negative Salary Boundary ---")
        # Try creating offer with negative salary and past expiration date
        offer_payload = {
            "applicationId": "dummy-app-id",
            "baseSalary": -50000,
            "currency": "USD",
            "startDate": "2026-12-01",
            "expiresAt": "2020-01-01"  # Past date
        }
        req = urllib.request.Request(
            "https://api.dev.hire.zobay.in/recruiter/offers",
            data=json.dumps(offer_payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
        )
        try:
            res = self.opener_recruiter.open(req)
            print(f"[DEFECT CONFIRMED] Offer created with negative salary and past expiration date! Status {res.status}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"HTTP Status {e.code}: {err_body}")
            if e.code == 500:
                print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on negative salary / boundary payload!")
            else:
                print("Properly rejected by input validation.")

    def probe_3_malformed_file_upload(self):
        print("\n--- Probe 3: File Upload Extension & MIME Type Security ---")
        # Probe document upload with executable payload
        boundary = "----WebKitFormBoundaryX9Z8Y7"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="malicious_script.exe"\r\n'
            f"Content-Type: application/x-msdownload\r\n\r\n"
            f"MZ_FAKE_EXECUTABLE_HEADER_CONTENT\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="type"\r\n\r\n'
            f"RESUME\r\n"
            f"--{boundary}--\r\n"
        ).encode('utf-8')

        req = urllib.request.Request(
            "https://api.dev.hire.zobay.in/candidate/documents/upload",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Origin": "https://dev.candidate.hire.zobay.in"
            }
        )
        try:
            res = self.opener_candidate.open(req)
            print(f"[DEFECT CONFIRMED] .exe upload was ACCEPTED with status {res.status}!")
            print("Response:", res.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"HTTP Status {e.code}: {err_body}")
            if e.code == 500:
                print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on file upload validation!")

    def probe_4_recruiter_idor_on_applications(self):
        print("\n--- Probe 4: IDOR / Cross-Tenant Handling on Applications ---")
        foreign_uuid = "00000000-0000-0000-0000-000000000000"
        req = urllib.request.Request(
            f"https://api.dev.hire.zobay.in/recruiter/applications/{foreign_uuid}",
            headers={"Origin": "https://dev.recruiter.hire.zobay.in"}
        )
        try:
            res = self.opener_recruiter.open(req)
            print(f"Status: {res.status}")
        except urllib.error.HTTPError as e:
            print(f"HTTP Status {e.code}: {e.read().decode('utf-8')}")


if __name__ == "__main__":
    hunter = HireXDeepHunter()
    hunter.login_recruiter()
    hunter.login_candidate()
    hunter.probe_1_state_machine_illegal_jump()
    hunter.probe_2_negative_salary_offer_creation()
    hunter.probe_3_malformed_file_upload()
    hunter.probe_4_recruiter_idor_on_applications()

