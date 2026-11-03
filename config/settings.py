import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # URLs
    RECRUITER_URL = os.getenv("RECRUITER_URL", "https://dev.recruiter.hire.zobay.in")
    INTERVIEWER_URL = os.getenv("INTERVIEWER_URL", "https://dev.interviewer.hire.zobay.in")
    CANDIDATE_URL = os.getenv("CANDIDATE_URL", "https://dev.candidate.hire.zobay.in")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.dev.hire.zobay.in")
    
    # Credentials
    RECRUITER_EMAIL = os.getenv("RECRUITER_EMAIL", "recruiter@hirex.dev")
    RECRUITER_PASSWORD = os.getenv("RECRUITER_PASSWORD", "Password123!")
    
    INTERVIEWER_EMAIL = os.getenv("INTERVIEWER_EMAIL", "rahul.sharma@hirex.dev")
    INTERVIEWER_PASSWORD = os.getenv("INTERVIEWER_PASSWORD", "Password123!")
    
    CANDIDATE_EMAIL = os.getenv("CANDIDATE_EMAIL", "rahul@hirex.dev")
    CANDIDATE_PASSWORD = os.getenv("CANDIDATE_PASSWORD", "Password123!")
    
    # Test execution
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "20000"))
    CAREER_SLUG = "hirex-demo-corp"

settings = Settings()

