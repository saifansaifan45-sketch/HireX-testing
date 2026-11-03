from playwright.sync_api import sync_playwright

def inspect_recruiter_network():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        requests_log = []
        page.on("request", lambda req: requests_log.append(f"{req.method} {req.url}"))
        
        page.goto("https://dev.recruiter.hire.zobay.in/login")
        page.fill("#email", "recruiter@hirex.dev")
        page.fill("#password", "Password123!")
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(3000)
        
        requests_log.clear() # clear login calls
        
        print("\nNavigating to /applicants...")
        page.goto("https://dev.recruiter.hire.zobay.in/applicants")
        page.wait_for_timeout(5000)
        
        print(f"Requests on /applicants ({len(requests_log)}):")
        for r in requests_log:
            if "hire.zobay.in" in r and "_next" not in r:
                print("  ", r)
                
        # Also check /jobs
        requests_log.clear()
        print("\nNavigating to /jobs...")
        page.goto("https://dev.recruiter.hire.zobay.in/jobs")
        page.wait_for_timeout(4000)
        print(f"Requests on /jobs ({len(requests_log)}):")
        for r in requests_log:
            if "hire.zobay.in" in r and "_next" not in r:
                print("  ", r)

        # Also check /interviews
        requests_log.clear()
        print("\nNavigating to /interviews...")
        page.goto("https://dev.recruiter.hire.zobay.in/interviews")
        page.wait_for_timeout(4000)
        print(f"Requests on /interviews ({len(requests_log)}):")
        for r in requests_log:
            if "hire.zobay.in" in r and "_next" not in r:
                print("  ", r)
                
        browser.close()

if __name__ == "__main__":
    inspect_recruiter_network()

