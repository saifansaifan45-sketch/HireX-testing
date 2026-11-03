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
    "https://api.dev.hire.zobay.in/recruiter/applications",
    headers={"Origin": "https://dev.recruiter.hire.zobay.in"}
)
res = opener.open(req)
data = json.loads(res.read().decode('utf-8'))
print("Applications type:", type(data))
if isinstance(data, list) and len(data) > 0:
    print("Application 0 keys:", list(data[0].keys()))
    print("Sample application 0:", json.dumps(data[0], indent=2))
elif isinstance(data, dict):
    print("Dict keys:", list(data.keys()))
    apps = data.get("applications", [])
    if apps:
        print("Application 0 keys:", list(apps[0].keys()))
        print("Sample application 0:", json.dumps(apps[0], indent=2))

