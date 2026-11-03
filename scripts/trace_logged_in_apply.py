from playwright.sync_api import sync_playwright

def trace_logged_in_apply():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Login Candidate
        page.goto("https://dev.candidate.hire.zobay.in/login")
        page.fill("#login-email", "rahul@hirex.dev")
        page.fill("#login-password", "Password123!")
        page.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(3000)
        
        requests = []
        page.on("request", lambda req: requests.append(f"{req.method} {req.url}"))
        
        # 2. Go to apply page
        apply_url = "https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp/jobs/job-fs-04/apply"
        print(f"Navigating to {apply_url}...")
        page.goto(apply_url)
        page.wait_for_timeout(4000)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        inputs = page.locator("input, textarea, select")
        print(f"Inputs count: {inputs.count()}")
        for i in range(inputs.count()):
            el = inputs.nth(i)
            print(f"  Input {i}: type={el.get_attribute('type')} name={el.get_attribute('name')} id={el.get_attribute('id')}")
            
        buttons = page.locator("button")
        print(f"Buttons count: {buttons.count()}")
        for i in range(buttons.count()):
            try:
                print("  Button:", buttons.nth(i).inner_text().strip())
            except:
                pass
                
        print("\nBackend API requests made:")
        for r in requests:
            if "hire.zobay.in" in r and "_next" not in r and "static" not in r:
                print("  ", r)
                
        browser.close()

if __name__ == "__main__":
    trace_logged_in_apply()

