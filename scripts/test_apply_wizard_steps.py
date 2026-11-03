from playwright.sync_api import sync_playwright

def test_apply_wizard_steps():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Login
        page.goto("https://dev.candidate.hire.zobay.in/login")
        page.fill("#login-email", "rahul@hirex.dev")
        page.fill("#login-password", "Password123!")
        page.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(3000)
        
        # 2. Go to apply wizard
        page.goto("https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp/jobs/job-fs-04/apply")
        page.wait_for_timeout(3000)
        
        # Click Continue without selecting resume
        print("Clicking Continue on Step 1 (Resume)...")
        continue_btn = page.locator('button:has-text("Continue")')
        continue_btn.click()
        page.wait_for_timeout(2000)
        
        # Check alerts / validation messages
        errors = page.locator('.text-red-500, .text-destructive, [role="alert"], p[class*="error"]')
        print(f"Validation errors ({errors.count()}):")
        for i in range(errors.count()):
            try:
                print("  -", errors.nth(i).inner_text().strip())
            except:
                pass
                
        # Click 'Reset draft'
        print("\nClicking 'Reset draft'...")
        reset_btn = page.locator('button:has-text("Reset draft")')
        if reset_btn.count() > 0:
            reset_btn.click()
            page.wait_for_timeout(2000)
            dialogs = page.locator('[role="dialog"], [class*="modal"]')
            print(f"Modal / Confirmation dialogs: {dialogs.count()}")
            if dialogs.count() > 0:
                print("  Dialog text:", dialogs.first.inner_text().strip().replace("\n", " "))
                
        browser.close()

if __name__ == "__main__":
    test_apply_wizard_steps()

