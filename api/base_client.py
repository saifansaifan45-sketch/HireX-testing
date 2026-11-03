import json
from playwright.sync_api import APIRequestContext
from typing import Optional, Dict, Any

class BaseAPIClient:
    def __init__(self, request_context: APIRequestContext, base_url: str):
        self.request = request_context
        self.base_url = base_url.rstrip("/")
        
    def _url(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
        
    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None):
        return self.request.get(self._url(endpoint), headers=headers, params=params)
        
    def post(self, endpoint: str, data: Optional[Any] = None, json_data: Optional[Any] = None, headers: Optional[Dict[str, str]] = None, multipart: Optional[Any] = None):
        req_headers = headers.copy() if headers else {}
        body = data
        if json_data is not None:
            body = json.dumps(json_data)
            req_headers["Content-Type"] = "application/json"
        return self.request.post(self._url(endpoint), data=body, headers=req_headers, multipart=multipart)
        
    def patch(self, endpoint: str, data: Optional[Any] = None, json_data: Optional[Any] = None, headers: Optional[Dict[str, str]] = None):
        req_headers = headers.copy() if headers else {}
        body = data
        if json_data is not None:
            body = json.dumps(json_data)
            req_headers["Content-Type"] = "application/json"
        return self.request.patch(self._url(endpoint), data=body, headers=req_headers)
        
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        return self.request.delete(self._url(endpoint), headers=headers)
