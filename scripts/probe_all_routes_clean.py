import httpx

API_BASE = "https://api.dev.hire.zobay.in"

# Login Recruiter to get cookie
c_rec = httpx.Client(verify=False)
r_rec = c_rec.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "recruiter@hirex.dev", "password": "Password123!"})
rec_cookie = r_rec.headers.get("set-cookie", "")

# Login Candidate to get cookie
c_cand = httpx.Client(verify=False)
r_cand = c_cand.post(f"{API_BASE}/api/auth/sign-in/email", json={"email": "rahul@hirex.dev", "password": "Password123!"}, headers={"Origin": "https://dev.candidate.hire.zobay.in"})
cand_cookie = r_cand.headers.get("set-cookie", "")

# Login Interviewer to get cookie
c_int = httpx.Client(verify=False)
r_int = c_int.post(f"{API_BASE}/auth/interviewer/login", json={"email": "rahul.sharma@hirex.dev", "password": "Password123!"})
int_cookie = r_int.headers.get("set-cookie", "")

routes = [
    ("GET", "/jobs"),
    ("GET", "/jobs/job-fs-04"),
    ("GET", "/jobs/job-fs-04/application-form"),
    ("GET", "/api/auth/get-session"),
    ("GET", "/search?q=test"),
    ("GET", "/candidate/applications"),
    ("GET", "/candidate/interviews"),
    ("GET", "/interviewer/interviews"),
    ("GET", "/interviewer/history"),
    ("GET", "/interviewer/profile"),
    ("GET", "/feeds/indeed-jobs.xml"),
    ("GET", "/public/career-domain?host=careers.hirex.dev"),
]

print(f"{'Method & Route':<35} | {'Unauth':<8} | {'Candidate':<10} | {'Interviewer':<12} | {'Recruiter':<10}")
print("-" * 85)

for method, route in routes:
    # 1. Fresh Unauth client
    with httpx.Client(verify=False) as c:
        s_unauth = c.request(method, f"{API_BASE}{route}").status_code
    # 2. Fresh Candidate client
    with httpx.Client(verify=False) as c:
        s_cand = c.request(method, f"{API_BASE}{route}", headers={"Cookie": cand_cookie}).status_code
    # 3. Fresh Interviewer client
    with httpx.Client(verify=False) as c:
        s_int = c.request(method, f"{API_BASE}{route}", headers={"Cookie": int_cookie}).status_code
    # 4. Fresh Recruiter client
    with httpx.Client(verify=False) as c:
        s_rec = c.request(method, f"{API_BASE}{route}", headers={"Cookie": rec_cookie}).status_code
        
    print(f"{method + ' ' + route:<35} | {s_unauth:<8} | {s_cand:<10} | {s_int:<12} | {s_rec:<10}")

