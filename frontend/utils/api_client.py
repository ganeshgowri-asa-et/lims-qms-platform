"""API client for communicating with the backend."""
import httpx
from typing import Dict, Any, List, Optional


class APIClient:
    """Client for making API requests to the backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"

        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    response = client.get(url, params=params)
                elif method == "POST":
                    response = client.post(url, json=data, params=params)
                elif method == "PUT":
                    response = client.put(url, json=data, params=params)
                elif method == "DELETE":
                    response = client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}

    # Document Management API calls
    def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document."""
        return self._make_request("POST", "/documents/", data=document_data)

    def get_documents(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of documents."""
        return self._make_request("GET", "/documents/", params={"skip": skip, "limit": limit})

    def get_document(self, document_id: int) -> Dict[str, Any]:
        """Get a specific document."""
        return self._make_request("GET", f"/documents/{document_id}")

    def update_document(self, document_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document."""
        return self._make_request("PUT", f"/documents/{document_id}", data=updates)

    def create_revision(self, document_id: int, revision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document revision."""
        return self._make_request("POST", f"/documents/{document_id}/revise", data=revision_data)

    def approve_document(self, document_id: int, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve a document."""
        return self._make_request("POST", f"/documents/{document_id}/approve", data=approval_data)

    def search_documents(
        self, search_term: Optional[str] = None, doc_type: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search documents."""
        params = {}
        if search_term:
            params["q"] = search_term
        if doc_type:
            params["doc_type"] = doc_type
        if status:
            params["status"] = status
        return self._make_request("GET", "/documents/search/", params=params)

    # Equipment Management API calls
    def create_equipment(self, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new equipment."""
        return self._make_request("POST", "/equipment/", data=equipment_data)

    def get_equipment_list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of equipment."""
        return self._make_request("GET", "/equipment/", params={"skip": skip, "limit": limit})

    def get_equipment(self, equipment_id: int) -> Dict[str, Any]:
        """Get specific equipment."""
        return self._make_request("GET", f"/equipment/{equipment_id}")

    def update_equipment(self, equipment_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update equipment."""
        return self._make_request("PUT", f"/equipment/{equipment_id}", data=updates)

    def create_calibration(self, equipment_id: int, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calibration record."""
        return self._make_request("POST", f"/equipment/{equipment_id}/calibration", data=calibration_data)

    def get_calibrations(self, equipment_id: int) -> List[Dict[str, Any]]:
        """Get calibration records for equipment."""
        return self._make_request("GET", f"/equipment/{equipment_id}/calibration")

    def create_maintenance(self, equipment_id: int, maintenance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create maintenance schedule."""
        return self._make_request("POST", f"/equipment/{equipment_id}/maintenance", data=maintenance_data)

    def get_maintenance(self, equipment_id: int) -> List[Dict[str, Any]]:
        """Get maintenance records for equipment."""
        return self._make_request("GET", f"/equipment/{equipment_id}/maintenance")

    def get_calibration_alerts(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get calibration alerts."""
        return self._make_request("GET", "/equipment/alerts/calibration", params={"days": days})

    def generate_qr_code(self, equipment_id: int) -> Dict[str, Any]:
        """Generate QR code for equipment."""
        return self._make_request("POST", f"/equipment/{equipment_id}/generate-qr")
