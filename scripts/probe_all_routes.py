import httpx

API_BASE = "https://api.dev.hire.zobay.in"
client = httpx.Client(verify=False, timeout=10.0)

# 1. Login Recruiter
r_rec = client.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "recruiter@hirex.dev", "password": "Password123!"})
rec_cookie = r_rec.headers.get("set-cookie", "")

# 2. Login Candidate
r_cand = client.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "rahul@hirex.dev", "password": "Password123!"}, headers={"Origin": "https://dev.candidate.hire.zobay.in"})
cand_cookie = r_cand.headers.get("set-cookie", "")

# 3. Login Interviewer
r_int = client.post(f"{API_BASE}/auth/interviewer/login", json={"email": "rahul.sharma@hirex.dev", "password": "Password123!"})
int_cookie = r_int.headers.get("set-cookie", "")

routes = [
    ("GET", "/jobs"),
    ("GET", "/jobs/job-fs-04"),
    ("GET", "/jobs/job-fs-04/application-form"),
    ("GET", "/api/auth/get-session"),
    ("GET", "/search?q=test"),
    ("GET", "/candidate/applications"),
    ("GET", "/candidate/documents"),
    ("GET", "/candidate/interviews"),
    ("GET", "/interviews"),
    ("GET", "/interviewer/interviews"),
    ("GET", "/interviews/my"),
    ("GET", "/recruiters/team"),
    ("GET", "/recruiters/documents"),
    ("GET", "/recruiters/applicants"),
    ("GET", "/reports"),
    ("GET", "/company"),
    ("GET", "/company/settings"),
    ("GET", "/feeds/indeed-jobs.xml"),
    ("GET", "/feeds/linkedin-jobs.xml"),
    ("GET", "/feeds/naukri-jobs.xml"),
    ("GET", "/public/career-domain?host=careers.hirex.dev"),
    ("GET", "/public/career-domain"),
]

print(f"{'Method & Route':<35} | {'Unauth':<8} | {'Candidate':<10} | {'Interviewer':<12} | {'Recruiter':<10}")
print("-" * 85)

for method, route in routes:
    # Unauth
    r_unauth = client.request(method, f"{API_BASE}{route}")
    # Candidate
    r_cand = client.request(method, f"{API_BASE}{route}", headers={"Cookie": cand_cookie})
    # Interviewer
    r_int = client.request(method, f"{API_BASE}{route}", headers={"Cookie": int_cookie})
    # Recruiter
    r_rec = client.request(method, f"{API_BASE}{route}", headers={"Cookie": rec_cookie})
    
    print(f"{method + ' ' + route:<35} | {r_unauth.status_code:<8} | {r_cand.status_code:<10} | {r_int.status_code:<12} | {r_rec.status_code:<10}")

