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

login_req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
    data=json.dumps({"email": "recruiter@hirex.dev", "password": "Password123!"}).encode('utf-8'),
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
)
opener.open(login_req)

req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/recruiter/applications/app-rahul-innovatex-01",
    headers={"Origin": "https://dev.recruiter.hire.zobay.in"}
)
res = opener.open(req)
data = json.loads(res.read().decode('utf-8'))
print("Single App resumeSnapshotUrl:", data.get("resumeSnapshotUrl"))
print("Single App resume.fileUrl:", data.get("resume", {}).get("fileUrl"))

