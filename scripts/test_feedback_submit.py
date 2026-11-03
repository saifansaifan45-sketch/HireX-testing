from playwright.sync_api import sync_playwright

def test_feedback_submit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        captured_requests = []
        page.on("request", lambda req: captured_requests.append((req.method, req.url, req.post_data)))
        
        # Login
        page.goto("https://dev.interviewer.hire.zobay.in/login?returnUrl=%2Fdashboard")
        page.fill("#login-email", "rahul.sharma@hirex.dev")
        page.fill("#login-password", "Password123!")
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(3000)
        
        # Go to feedback
        interview_id = "185f2a88-8d6f-4c0b-bb19-a064877e499c"
        page.goto(f"https://dev.interviewer.hire.zobay.in/interviews/{interview_id}/feedback")
        page.wait_for_timeout(3000)
        
        captured_requests.clear()
        
        # Select Recommendation (e.g. HIRE or first radio)
        radios = page.locator('input[name="recommendation"]')
        if radios.count() > 0:
            radios.nth(0).check()
            
        # Fill textareas
        textareas = page.locator("textarea")
        if textareas.count() >= 1:
            textareas.nth(0).fill("Great architectural knowledge and coding skills.")
        if textareas.count() >= 2:
            textareas.nth(1).fill("None observed during 45 min call.")
            
        # Click submit button
        submit_btn = page.locator('button:has-text("Submit"), button[type="submit"]')
        print(f"Submit button found: {submit_btn.count()}")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(5000)
            
        print("Captured API requests during submission:")
        for method, url, post_data in captured_requests:
            if "hire.zobay.in" in url and "_next" not in url:
                print(f"  {method} {url}")
                print(f"  Payload: {post_data}")
                
        # Check for error banners or toasts on page
        alerts = page.locator('[role="alert"], .text-red-500, .text-destructive, [class*="toast"]')
        print(f"Alerts / Toasts visible: {alerts.count()}")
        for i in range(alerts.count()):
            try:
                print(f"  Alert {i}: {alerts.nth(i).inner_text().strip()}")
            except Exception:
                pass
                
        browser.close()

if __name__ == "__main__":
    test_feedback_submit()

