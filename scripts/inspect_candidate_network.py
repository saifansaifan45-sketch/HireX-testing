from playwright.sync_api import sync_playwright

def inspect_apply_network():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        requests = []
        page.on("request", lambda req: requests.append(f"{req.method} {req.url}"))
        page.on("response", lambda res: print(f"  [NET] {res.request.method} {res.url} -> {res.status}"))

        print("1. Login as Candidate...")
        page.goto("https://dev.candidate.hire.zobay.in/login")
        page.fill("#login-email", "rahul@hirex.dev")
        page.fill("#login-password", "Password123!")
        page.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(3000)

        print("\n2. Go to Apply Wizard...")
        page.goto("https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp/jobs/job-fs-04/apply")
        page.wait_for_timeout(3500)

        # Inspect network endpoints called by wizard
        print("\nAPI requests during Apply Wizard load:")
        for r in requests:
            if "hire.zobay.in" in r:
                print("  ", r)

        browser.close()

if __name__ == "__main__":
    inspect_apply_network()

