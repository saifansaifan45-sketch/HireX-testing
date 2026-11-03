from playwright.sync_api import sync_playwright

def inspect_invite_modal():
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
        
        # Click Invite Team Member
        btn = page.locator('button:has-text("Invite Team Member")')
        btn.click()
        page.wait_for_timeout(2000)
        
        # Check inputs visible
        inputs = page.locator("input, select")
        print(f"Inputs visible after clicking Invite: {inputs.count()}")
        for i in range(inputs.count()):
            el = inputs.nth(i)
            print(f"  Field {i}: type={el.get_attribute('type')} name={el.get_attribute('name')} id={el.get_attribute('id')} placeholder={el.get_attribute('placeholder')}")
            
        browser.close()

if __name__ == "__main__":
    inspect_invite_modal()

