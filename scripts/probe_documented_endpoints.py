"""
Deep Bug Hunter Probe against Exact API Endpoints Catalog:
1. PATCH /applications/:id/status (Invalid transitions & unhandled enum exceptions)
2. POST /recruiters/offers/generate (Boundary salary & schema validation)
3. POST /candidate/documents/upload (File validation)
4. POST /webhooks/schedular (HMAC signature verification)
5. POST /interviews/booking (Invalid / past slot booking)
"""
import urllib.request
import urllib.parse
import http.cookiejar
import json
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

cj_recruiter = http.cookiejar.CookieJar()
opener_recruiter = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj_recruiter),
    urllib.request.HTTPSHandler(context=ssl_ctx)
)

cj_candidate = http.cookiejar.CookieJar()
opener_candidate = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj_candidate),
    urllib.request.HTTPSHandler(context=ssl_ctx)
)

# 1. Login Recruiter
login_req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
    data=json.dumps({"email": "recruiter@hirex.dev", "password": "Password123!"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
)
res = opener_recruiter.open(login_req)
print("[AUTH] Recruiter Login:", res.status)

# 2. Login Candidate
login_cand = urllib.request.Request(
    "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
    data=json.dumps({"email": "rahul@hirex.dev", "password": "Password123!"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"}
)
res_cand = opener_candidate.open(login_cand)
print("[AUTH] Candidate Login:", res_cand.status)

# -----------------------------------------------------------------
# Probe 1: PATCH /applications/:id/status with invalid enum status
# -----------------------------------------------------------------
print("\n--- Probe 1: PATCH /applications/:id/status (Invalid Enum Status) ---")
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/applications/app-rahul-innovatex-01/status",
    data=json.dumps({"status": "INVALID_STATUS_ENUM"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"},
    method="PATCH"
)
try:
    r = opener_recruiter.open(req)
    print("Status:", r.status, r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP Status {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on invalid status enum!")

# -----------------------------------------------------------------
# Probe 2: PATCH /applications/:id/status with backward state jump
# -----------------------------------------------------------------
print("\n--- Probe 2: PATCH /applications/:id/status (Backward State Jump) ---")
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/applications/app-rahul-innovatex-01/status",
    data=json.dumps({"status": "APPLIED"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"},
    method="PATCH"
)
try:
    r = opener_recruiter.open(req)
    print(f"Status: {r.status}, Body: {r.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP Status {e.code}: {body}")

# -----------------------------------------------------------------
# Probe 3: POST /recruiters/offers/generate with negative salary
# -----------------------------------------------------------------
print("\n--- Probe 3: POST /recruiters/offers/generate (Negative Salary) ---")
offer_payload = {
    "applicationId": "app-rahul-innovatex-01",
    "baseSalary": -50000,
    "currency": "INR",
    "designation": "Staff Engineer"
}
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/recruiters/offers/generate",
    data=json.dumps(offer_payload).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
)
try:
    r = opener_recruiter.open(req)
    print(f"Status: {r.status}, Body: {r.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP Status {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on offer generation!")

# -----------------------------------------------------------------
# Probe 4: POST /webhooks/schedular without HMAC Signature
# -----------------------------------------------------------------
print("\n--- Probe 4: POST /webhooks/schedular (Missing / Forged Signature) ---")
webhook_payload = {
    "event": "meeting.completed",
    "meetingId": "meet-12345",
    "status": "COMPLETED"
}
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/webhooks/schedular",
    data=json.dumps(webhook_payload).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(req)
    print(f"[DEFECT CONFIRMED] Webhook accepted without HMAC signature! Status {r.status}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP Status {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Webhook handler crashed with HTTP 500 on missing signature header!")

# -----------------------------------------------------------------
# Probe 5: POST /interviews/booking without authentication
# -----------------------------------------------------------------
print("\n--- Probe 5: POST /interviews/booking (Unauthenticated Booking) ---")
booking_payload = {
    "slotId": "slot-test-01",
    "candidateEmail": "attacker@evil.com"
}
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/interviews/booking",
    data=json.dumps(booking_payload).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(req)
    print(f"Status: {r.status}, Body: {r.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP Status {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on booking attempt!")

