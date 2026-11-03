from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class ApplicationsClient(BaseAPIClient):
    def submit_application(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/applications", json_data=payload, headers=headers)
        
    def submit_guest_resume(self, files: Dict[str, Any], data: Dict[str, str]):
        return self.post("/public/guest-resume", multipart={**files, **data})
        
    def update_application_status(self, application_id: str, status: str, headers: Optional[Dict[str, str]] = None):
        return self.patch(f"/applications/{application_id}/status", json_data={"status": status}, headers=headers)
