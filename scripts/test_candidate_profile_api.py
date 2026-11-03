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

# 1. Fetch current profile
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/me",
    headers={"Origin": "https://dev.candidate.hire.zobay.in"}
)
res = opener.open(req)
profile = json.loads(res.read().decode('utf-8'))
print("Current profile name:", profile.get("name") or profile.get("user", {}).get("name"))

# 2. Try PATCH /candidate/me with unexpected payload (null name, or number for string)
patch_payload = {
    "name": 12345678,
    "phone": ["invalid", "type"]
}
req2 = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/me",
    data=json.dumps(patch_payload).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"},
    method="PATCH"
)
try:
    r2 = opener.open(req2)
    print("PATCH /candidate/me status:", r2.status, r2.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"PATCH /candidate/me HTTP {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on unexpected profile types!")

