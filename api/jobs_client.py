from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class JobsClient(BaseAPIClient):
    def get_public_jobs(self, search: Optional[str] = None, location: Optional[str] = None, work_mode: Optional[str] = None):
        params = {}
        if search: params["search"] = search
        if location: params["location"] = location
        if work_mode: params["workMode"] = work_mode
        return self.get("/jobs", params=params)
        
    def get_job_by_id(self, job_id: str):
        return self.get(f"/jobs/{job_id}")
        
    def get_application_form_schema(self, job_id: str):
        return self.get(f"/jobs/{job_id}/application-form")
        
    def create_recruiter_job(self, job_payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/recruiters/jobs", json_data=job_payload, headers=headers)
