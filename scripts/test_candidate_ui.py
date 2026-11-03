from playwright.sync_api import sync_playwright

def test_candidate_login_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://dev.candidate.hire.zobay.in/login')
        print("Candidate Login Page Title:", page.title())
        inputs = page.locator('input').all()
        for inp in inputs:
            print(f"  - input type={inp.get_attribute('type')} id={inp.get_attribute('id')}")
        # Try filling email and password
        page.fill('input[type="email"]', 'rahul@hirex.dev')
        page.fill('input[type="password"]', 'Password123!')
        page.click('button:has-text("Sign In"), button:has-text("Login")')
        page.wait_for_timeout(5000)
        print("Candidate Logged in URL:", page.url)
        print("Candidate Logged in Title:", page.title())
        nav_links = page.locator('a').all()
        print(f"Links ({len(nav_links)}):")
        for link in nav_links[:15]:
            href = link.get_attribute('href')
            text = link.inner_text().strip().replace('\n', ' ')
            if text or href:
                print(f"  - '{text}' -> {href}")
        browser.close()

if __name__ == '__main__':
    test_candidate_login_ui()

