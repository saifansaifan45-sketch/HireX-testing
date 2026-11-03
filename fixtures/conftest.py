import os
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, APIRequestContext
from config.settings import settings
from api.auth_client import AuthClient
from api.jobs_client import JobsClient
from api.applications_client import ApplicationsClient
from api.interviews_client import InterviewsClient
from api.offers_client import OffersClient
from api.documents_client import DocumentsClient

def pytest_addoption(parser):
    parser.addoption(
        "--headed", action="store_true", default=False, help="Run browser tests in headed mode"
    )
    parser.addoption(
        "--slowmo", type=int, default=0, help="Slow down Playwright operations by specified milliseconds"
    )

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance, request) -> Browser:
    # Check if CLI flag --headed is passed or HEADLESS env var is set to false
    is_headed_cli = request.config.getoption("--headed")
    slow_mo = request.config.getoption("--slowmo")
    
    is_headless = False if is_headed_cli else settings.HEADLESS
    
    browser = playwright_instance.chromium.launch(
        headless=is_headless,
        slow_mo=slow_mo,
        args=["--disable-dev-shm-usage", "--no-sandbox"]
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser) -> BrowserContext:
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True
    )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context) -> Page:
    page = context.new_page()
    page.set_default_timeout(settings.DEFAULT_TIMEOUT)
    yield page
    page.close()

@pytest.fixture(scope="session")
def api_request_context(playwright_instance) -> APIRequestContext:
    request_context = playwright_instance.request.new_context(
        base_url=settings.API_BASE_URL,
        ignore_https_errors=True
    )
    yield request_context
    request_context.dispose()

@pytest.fixture(scope="session")
def auth_client(api_request_context) -> AuthClient:
    return AuthClient(api_request_context, settings.API_BASE_URL)

@pytest.fixture(scope="session")
def jobs_client(api_request_context) -> JobsClient:
    return JobsClient(api_request_context, settings.API_BASE_URL)

@pytest.fixture(scope="session")
def applications_client(api_request_context) -> ApplicationsClient:
    return ApplicationsClient(api_request_context, settings.API_BASE_URL)

@pytest.fixture(scope="session")
def interviews_client(api_request_context) -> InterviewsClient:
    return InterviewsClient(api_request_context, settings.API_BASE_URL)

@pytest.fixture(scope="session")
def offers_client(api_request_context) -> OffersClient:
    return OffersClient(api_request_context, settings.API_BASE_URL)

@pytest.fixture(scope="session")
def documents_client(api_request_context) -> DocumentsClient:
    return DocumentsClient(api_request_context, settings.API_BASE_URL)
