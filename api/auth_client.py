from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class AuthClient(BaseAPIClient):
    def sign_in_email(self, email: str, password: str, origin: str = "https://dev.candidate.hire.zobay.in"):
        headers = {"Origin": origin}
        return self.post("/api/auth/sign-in/email", json_data={"email": email, "password": password}, headers=headers)
        
    def sign_up_email(self, name: str, email: str, password: str, origin: str = "https://dev.candidate.hire.zobay.in"):
        headers = {"Origin": origin}
        return self.post("/api/auth/sign-up/email", json_data={"name": name, "email": email, "password": password}, headers=headers)
        
    def interviewer_login(self, email: str, password: str, remember_me: bool = True):
        return self.post("/auth/interviewer/login", json_data={"email": email, "password": password, "rememberMe": remember_me})
        
    def get_session(self, headers: Optional[Dict[str, str]] = None):
        return self.get("/api/auth/get-session", headers=headers)
        
    def sign_out(self, origin: str = "https://dev.candidate.hire.zobay.in"):
        headers = {"Origin": origin}
        return self.post("/api/auth/sign-out", headers=headers)
