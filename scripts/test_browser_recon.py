import os
from playwright.sync_api import sync_playwright

def inspect_portals():
    portals = [
        ('Recruiter Login', 'https://dev.recruiter.hire.zobay.in/login'),
        ('Interviewer Login', 'https://dev.interviewer.hire.zobay.in/login?returnUrl=%2Fdashboard'),
        ('Candidate Career Page', 'https://dev.candidate.hire.zobay.in/careers/hirex-demo-corp')
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for label, url in portals:
            print(f"\n=================== {label} ({url}) ===================")
            page = browser.new_page()
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                print(f"Title: {page.title()}")
                print(f"URL: {page.url}")
                inputs = page.locator('input').all()
                print(f"Inputs ({len(inputs)}):")
                for inp in inputs:
                    print(f"  - type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}")
                buttons = page.locator('button').all()
                print(f"Buttons ({len(buttons)}):")
                for btn in buttons[:8]:
                    text = btn.inner_text().strip().replace('\n', ' ')
                    print(f"  - button: '{text}'")
            except Exception as e:
                print(f"Error inspecting {url}: {e}")
            finally:
                page.close()
        browser.close()

if __name__ == '__main__':
    inspect_portals()

