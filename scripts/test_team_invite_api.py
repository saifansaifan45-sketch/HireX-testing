import urllib.request
import urllib.parse
import http.cookiejar
import json

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

login_data = json.dumps({"email": "recruiter@hirex.dev", "password": "Password123!"}).encode('utf-8')
req = urllib.request.Request(
    "https://api.dev.hire.zobay.in/api/auth/sign-in/email",
    data=login_data,
    headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
)
res = opener.open(req)
print("Login status:", res.status)

def send_invite(payload):
    req = urllib.request.Request(
        "https://api.dev.hire.zobay.in/recruiter/team/invite",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", "Origin": "https://dev.recruiter.hire.zobay.in"}
    )
    try:
        r = opener.open(req)
        print("Success:", r.status, r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}:", e.read().decode('utf-8'))

print("\n1. Duplicate invite:")
send_invite({"email": "recruiter@hirex.dev", "role": "MEMBER"})

print("\n2. Invalid role invite:")
send_invite({"email": "superadmin_test@hirex.dev", "role": "SUPER_ADMIN"})

print("\n3. Invalid email format:")
send_invite({"email": "not-an-email", "role": "MEMBER"})
