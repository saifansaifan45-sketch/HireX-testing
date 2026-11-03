from playwright.sync_api import sync_playwright

def inspect_team_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Login recruiter
        page.goto("https://dev.recruiter.hire.zobay.in/login")
        page.fill("#email", "recruiter@hirex.dev")
        page.fill("#password", "Password123!")
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(3000)
        
        # Navigate to /team
        page.goto("https://dev.recruiter.hire.zobay.in/team")
        page.wait_for_timeout(3000)
        
        print("Team Page URL:", page.url)
        print("Team Page Title:", page.title())
        
        buttons = page.locator("button")
        print(f"Buttons found ({buttons.count()}):")
        for i in range(buttons.count()):
            try:
                print("  -", buttons.nth(i).inner_text().strip())
            except:
                pass
                
        # Look for invite button
        invite_btn = page.locator('button:has-text("Invite"), button:has-text("Add Member"), button:has-text("New Member")')
        print(f"Invite button matches: {invite_btn.count()}")
        if invite_btn.count() > 0:
            invite_btn.first.click()
            page.wait_for_timeout(2000)
            dialogs = page.locator('[role="dialog"], [class*="modal"]')
            print(f"Invite dialog count: {dialogs.count()}")
            if dialogs.count() > 0:
                print("Dialog HTML / text:", dialogs.first.inner_text().strip().replace("\n", " "))
                
        browser.close()

if __name__ == "__main__":
    inspect_team_page()

