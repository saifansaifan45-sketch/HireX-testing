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

# Test 1: Empty name
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/me",
    data=json.dumps({"name": ""}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"},
    method="PUT"
)
try:
    r = opener.open(req)
    print("Empty name PUT status:", r.status, r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Empty name PUT HTTP {e.code}: {e.read().decode('utf-8')}")

# Test 2: Huge 100KB string
huge_str = "A" * 100000
req2 = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/me",
    data=json.dumps({"name": huge_str}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"},
    method="PUT"
)
try:
    r2 = opener.open(req2)
    print("100KB name PUT status:", r2.status)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"100KB name PUT HTTP {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on 100KB string payload!")

