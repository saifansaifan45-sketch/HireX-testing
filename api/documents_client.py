from .base_client import BaseAPIClient
from typing import Dict, Any, Optional

class DocumentsClient(BaseAPIClient):
    def upload_document(self, application_id: str, doc_type: str, file_payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        return self.post("/candidate/documents/upload", multipart={"applicationId": application_id, "type": doc_type, **file_payload}, headers=headers)
        
    def verify_document(self, document_id: str, headers: Optional[Dict[str, str]] = None):
        return self.patch(f"/recruiters/documents/{document_id}/verify", headers=headers)
        
    def reject_document(self, document_id: str, reason: str, headers: Optional[Dict[str, str]] = None):
        return self.patch(f"/recruiters/documents/{document_id}/reject", json_data={"reason": reason}, headers=headers)
