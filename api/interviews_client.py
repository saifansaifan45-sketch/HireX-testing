from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class InterviewsClient(BaseAPIClient):
    def save_availability(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/interviews/availability", json_data=payload, headers=headers)
        
    def generate_slots(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/interviews/slots/generate", json_data=payload, headers=headers)
        
    def book_slot(self, slot_id: str, headers: Optional[Dict[str, str]] = None):
        return self.post("/interviews/booking", json_data={"slotId": slot_id}, headers=headers)
        
    def submit_feedback(self, interview_id: str, feedback_payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post(f"/interviews/{interview_id}/feedback", json_data=feedback_payload, headers=headers)
