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

# Probe POST /candidate/resume with empty body
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/resume",
    data=b"{}",
    headers={"Content-Type": "application/json", "Origin": "https://dev.candidate.hire.zobay.in"}
)
try:
    r = opener.open(req)
    print("Empty POST /candidate/resume status:", r.status, r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"Empty POST /candidate/resume HTTP {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on empty resume POST!")

# Probe POST /candidate/resume with malformed multipart
boundary = "----WebKitFormBoundaryUpload"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test.sh"\r\n'
    f"Content-Type: application/x-sh\r\n\r\n"
    f"echo 'malicious payload'\r\n"
    f"--{boundary}--\r\n"
).encode('utf-8')

req2 = urllib.request.Request(
    "https://api.dev.hire.zobay.in/candidate/resume",
    data=body,
    headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Origin": "https://dev.candidate.hire.zobay.in"
    }
)
try:
    r2 = opener.open(req2)
    print(f"Shell script upload status {r2.status}: {r2.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"Shell script upload HTTP {e.code}: {body}")
    if e.code == 500:
        print("[DEFECT CONFIRMED] Server crashed with HTTP 500 on shell script upload!")

