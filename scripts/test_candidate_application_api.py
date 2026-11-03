import urllib.request
import json
import http.cookiejar
import ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ssl_ctx)
)

login_cand = urllib.request.Request(
    "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
    data=json.dumps({"email": "rahul@hirex.dev", "password": "Password123!"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"}
)
opener.open(login_cand)

def test_apply(payload, label):
    print(f"\n--- Testing: {label} ---")
    req = urllib.request.Request(
        "https://api.dev.hire.zobay.in/applications",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"}
    )
    try:
        r = opener.open(req)
        print("Success:", r.status, r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Status {e.code}:", e.read().decode('utf-8'))

# Test 1: Empty payload
test_apply({}, "Empty payload")

# Test 2: Non-existent Job ID
test_apply({"jobId": "non-existent-job-uuid-12345", "formData": {}}, "Non-existent Job ID")

# Test 3: SQL Injection in jobId
test_apply({"jobId": "' OR '1'='1' --", "formData": {}}, "SQL Injection in Job ID")

