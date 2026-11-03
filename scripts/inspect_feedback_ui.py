from playwright.sync_api import sync_playwright

def inspect_feedback_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # 1. Login interviewer
        page.goto("https://dev.interviewer.hire.zobay.in/login?returnUrl=%2Fdashboard")
        page.fill("#login-email", "rahul.sharma@hirex.dev")
        page.fill("#login-password", "Password123!")
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(3000)
        
        # 2. Navigate to feedback page
        interview_id = "185f2a88-8d6f-4c0b-bb19-a064877e499c"
        print(f"Navigating to /interviews/{interview_id}/feedback...")
        page.goto(f"https://dev.interviewer.hire.zobay.in/interviews/{interview_id}/feedback")
        page.wait_for_timeout(4000)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        print("Inputs found:", page.locator("input, textarea, select").count())
        for i in range(page.locator("input, textarea, select").count()):
            el = page.locator("input, textarea, select").nth(i)
            print(f"  Field {i}: tag={el.evaluate('e => e.tagName')} name={el.get_attribute('name')} placeholder={el.get_attribute('placeholder')}")
            
        buttons = page.locator("button").all()
        print(f"Buttons ({len(buttons)}):")
        for b in buttons:
            print("  -", b.inner_text().strip().replace("\n", " "))
            
        print("\nConsole logs:")
        for log in console_logs:
            print("  ", log)
            
        browser.close()

if __name__ == "__main__":
    inspect_feedback_ui()

