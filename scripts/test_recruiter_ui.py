from playwright.sync_api import sync_playwright

def test_recruiter_login_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://dev.recruiter.hire.zobay.in/login')
        page.fill('#email', 'recruiter@hirex.dev')
        page.fill('#password', 'Password123!')
        page.click('button:has-text("Sign In")')
        page.wait_for_timeout(5000)
        print("Logged in URL:", page.url)
        print("Logged in Title:", page.title())
        # Print navigation links
        nav_links = page.locator('a').all()
        print(f"Links ({len(nav_links)}):")
        for link in nav_links[:15]:
            href = link.get_attribute('href')
            text = link.inner_text().strip().replace('\n', ' ')
            if text or href:
                print(f"  - '{text}' -> {href}")
        browser.close()

if __name__ == '__main__':
    test_recruiter_login_ui()

