from playwright.sync_api import sync_playwright

def test_team_invite_validations():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://dev.recruiter.hire.zobay.in/login")
        page.fill("#email", "recruiter@hirex.dev")
        page.fill("#password", "Password123!")
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(3000)
        
        page.goto("https://dev.recruiter.hire.zobay.in/team")
        page.wait_for_timeout(3000)
        
        # 1. Open Invite Modal
        page.click('button:has-text("Invite Team Member")')
        page.wait_for_timeout(1000)
        
        # 2. Try submitting empty email
        print("Test 1: Submitting with empty email...")
        send_btn = page.locator('button:has-text("Send Invitation"), button:has-text("Invite")').last
        send_btn.click()
        page.wait_for_timeout(1000)
        
        # 3. Try submitting existing recruiter email (duplicate)
        print("Test 2: Submitting duplicate existing email (recruiter@hirex.dev)...")
        email_inp = page.locator('input[placeholder="colleague@company.com"]')
        email_inp.fill("recruiter@hirex.dev")
        send_btn.click()
        page.wait_for_timeout(3000)
        
        # Check alerts / toasts
        alerts = page.locator('[role="alert"], .text-red-500, .text-destructive, div[class*="toast"]')
        print(f"Alerts / error banners visible: {alerts.count()}")
        for i in range(alerts.count()):
            try:
                print("  -", alerts.nth(i).inner_text().strip())
            except:
                pass
                
        browser.close()

if __name__ == "__main__":
    test_team_invite_validations()

