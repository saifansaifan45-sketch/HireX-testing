from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class OffersClient(BaseAPIClient):
    def generate_offer(self, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/recruiters/offers/generate", json_data=payload, headers=headers)
        
    def accept_offer(self, offer_id: str, signature: str, headers: Optional[Dict[str, str]] = None):
        return self.post(f"/candidate/offers/{offer_id}/accept", json_data={"signature": signature}, headers=headers)
