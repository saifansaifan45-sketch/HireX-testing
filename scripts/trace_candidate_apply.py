from playwright.sync_api import sync_playwright

def trace_candidate_apply():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        requests = []
        page.on("request", lambda req: requests.append(f"{req.method} {req.url}"))
        
        print("Navigating to career page...")
        page.goto("https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp")
        page.wait_for_timeout(3000)
        
        # Click on first job card
        job_buttons = page.locator('button:has-text("Developer"), button:has-text("Engineer")')
        print(f"Job cards found: {job_buttons.count()}")
        if job_buttons.count() > 0:
            job_buttons.first.click()
            page.wait_for_timeout(3000)
            print("Current URL after click:", page.url)
            
            # Look for Apply Now button
            apply_btn = page.locator('button:has-text("Apply"), a:has-text("Apply")')
            print(f"Apply buttons found: {apply_btn.count()}")
            for i in range(apply_btn.count()):
                try:
                    print("  Apply CTA:", apply_btn.nth(i).inner_text().strip())
                except:
                    pass
            if apply_btn.count() > 0:
                requests.clear()
                apply_btn.first.click()
                page.wait_for_timeout(4000)
                print("URL after clicking Apply:", page.url)
                print("Requests made:")
                for r in requests:
                    if "hire.zobay.in" in r and "_next" not in r:
                        print("  ", r)
                        
        browser.close()

if __name__ == "__main__":
    trace_candidate_apply()

