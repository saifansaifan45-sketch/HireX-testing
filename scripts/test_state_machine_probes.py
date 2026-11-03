import httpx

client = httpx.Client(verify=False)

r_rec = client.post("https://api.dev.hire.zobay.in/api/auth/sign-in/email", json={"email": "recruiter@hirex.dev", "password": "Password123!"})
rec_cookie = r_rec.headers.get("set-cookie", "")

app_id = "app-rahul-innovatex-01"

headers = {"Cookie": rec_cookie, "Origin": "https://dev.recruiter.hire.zobay.in"}

# 1. Advance to OFFER_STAGE while interview is open
r_offer = client.patch(f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/status", json={"status": "OFFER_STAGE"}, headers=headers)
print("ADVANCE TO OFFER_STAGE:", r_offer.status_code, r_offer.text)

# 2. Advance directly to HIRED (bypassing document verification FR-020)
r_hired = client.patch(f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/status", json={"status": "HIRED"}, headers=headers)
print("ADVANCE DIRECTLY TO HIRED:", r_hired.status_code, r_hired.text)

# 3. Advance to invalid status string
r_invalid = client.patch(f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/status", json={"status": "SUPER_HIRED"}, headers=headers)
print("ADVANCE TO INVALID STATUS:", r_invalid.status_code, r_invalid.text)

# 4. Advance with integer status
r_int = client.patch(f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/status", json={"status": 12345}, headers=headers)
print("ADVANCE WITH INTEGER STATUS:", r_int.status_code, r_int.text)

# 5. Candidate trying to call this recruiter status endpoint
r_cand = client.post("https://api.dev.hire.zobay.in/api/auth/sign-in/email", json={"email": "rahul@hirex.dev", "password": "Password123!"}, headers={"Origin": "https://dev.candidate.hire.zobay.in"})
cand_cookie = r_cand.headers.get("set-cookie", "")
r_cand_hack = client.patch(f"https://api.dev.hire.zobay.in/recruiter/applications/{app_id}/status", json={"status": "HIRED"}, headers={"Cookie": cand_cookie, "Origin": "https://dev.candidate.hire.zobay.in"})
print("CANDIDATE PRIVILEGE ESCALATION ATTEMPT:", r_cand_hack.status_code, r_cand_hack.text)

