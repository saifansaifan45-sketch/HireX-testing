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

for method in ["PUT", "POST"]:
    req = urllib.request.Request(
        "https://api.dev.hire.zobay.in/candidate/me",
        data=json.dumps({"name": 12345}).encode('utf-8'),
        headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"},
        method=method
    )
    try:
        r = opener.open(req)
        print(f"{method} /candidate/me status:", r.status)
    except urllib.error.HTTPError as e:
        print(f"{method} /candidate/me HTTP {e.code}: {e.read().decode('utf-8')}")

