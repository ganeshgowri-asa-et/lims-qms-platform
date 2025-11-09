"""API client utilities for making requests to the backend."""

import requests
from typing import Optional, Dict, Any, List
from config import settings


class APIClient:
    """Client for interacting with the backend API."""

    def __init__(self):
        self.base_url = f"http://{settings.API_HOST}:{settings.API_PORT}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 204:
            return {"success": True}
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text or "Unknown error"
            raise Exception(f"API Error ({response.status_code}): {error_detail}")

    # =================== Non-Conformance Endpoints ===================

    def create_nc(self, nc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Non-Conformance."""
        response = requests.post(f"{self.base_url}/api/nc/", json=nc_data)
        return self._handle_response(response)

    def get_ncs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all Non-Conformances."""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if severity:
            params["severity"] = severity

        response = requests.get(f"{self.base_url}/api/nc/", params=params)
        return self._handle_response(response)

    def get_nc_by_id(self, nc_id: int) -> Dict[str, Any]:
        """Get a specific Non-Conformance by ID."""
        response = requests.get(f"{self.base_url}/api/nc/{nc_id}")
        return self._handle_response(response)

    def get_nc_by_number(self, nc_number: str) -> Dict[str, Any]:
        """Get a specific Non-Conformance by number."""
        response = requests.get(f"{self.base_url}/api/nc/number/{nc_number}")
        return self._handle_response(response)

    def update_nc(self, nc_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Non-Conformance."""
        response = requests.put(f"{self.base_url}/api/nc/{nc_id}", json=update_data)
        return self._handle_response(response)

    def delete_nc(self, nc_id: int) -> Dict[str, Any]:
        """Delete a Non-Conformance."""
        response = requests.delete(f"{self.base_url}/api/nc/{nc_id}")
        return self._handle_response(response)

    def get_nc_statistics(self) -> Dict[str, Any]:
        """Get NC statistics."""
        response = requests.get(f"{self.base_url}/api/nc/statistics")
        return self._handle_response(response)

    # =================== Root Cause Analysis Endpoints ===================

    def create_rca(self, rca_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Root Cause Analysis."""
        response = requests.post(f"{self.base_url}/api/rca/", json=rca_data)
        return self._handle_response(response)

    def get_rca_by_id(self, rca_id: int) -> Dict[str, Any]:
        """Get a specific RCA by ID."""
        response = requests.get(f"{self.base_url}/api/rca/{rca_id}")
        return self._handle_response(response)

    def get_rcas_by_nc(self, nc_id: int) -> List[Dict[str, Any]]:
        """Get all RCAs for a specific NC."""
        response = requests.get(f"{self.base_url}/api/rca/nc/{nc_id}")
        return self._handle_response(response)

    def update_rca(self, rca_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an RCA."""
        response = requests.put(f"{self.base_url}/api/rca/{rca_id}", json=update_data)
        return self._handle_response(response)

    def approve_rca(self, rca_id: int, approved_by: str, comments: Optional[str] = None) -> Dict[str, Any]:
        """Approve an RCA."""
        params = {"approved_by": approved_by}
        if comments:
            params["comments"] = comments
        response = requests.post(f"{self.base_url}/api/rca/{rca_id}/approve", params=params)
        return self._handle_response(response)

    def get_5why_template(self) -> List[Dict[str, Any]]:
        """Get 5-Why template."""
        response = requests.get(f"{self.base_url}/api/rca/templates/5why")
        return self._handle_response(response)

    def get_fishbone_template(self) -> Dict[str, Any]:
        """Get Fishbone template."""
        response = requests.get(f"{self.base_url}/api/rca/templates/fishbone")
        return self._handle_response(response)

    def get_ai_suggestions(
        self,
        nc_description: str,
        problem_details: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI root cause suggestions."""
        data = {
            "nc_description": nc_description,
            "problem_details": problem_details,
            "context": context
        }
        response = requests.post(f"{self.base_url}/api/rca/ai/suggestions", json=data)
        return self._handle_response(response)

    # =================== CAPA Endpoints ===================

    def create_capa(self, capa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new CAPA Action."""
        response = requests.post(f"{self.base_url}/api/capa/", json=capa_data)
        return self._handle_response(response)

    def get_capas(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        capa_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all CAPA Actions."""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if capa_type:
            params["capa_type"] = capa_type

        response = requests.get(f"{self.base_url}/api/capa/", params=params)
        return self._handle_response(response)

    def get_capa_by_id(self, capa_id: int) -> Dict[str, Any]:
        """Get a specific CAPA by ID."""
        response = requests.get(f"{self.base_url}/api/capa/{capa_id}")
        return self._handle_response(response)

    def get_capas_by_nc(self, nc_id: int) -> List[Dict[str, Any]]:
        """Get all CAPAs for a specific NC."""
        response = requests.get(f"{self.base_url}/api/capa/nc/{nc_id}")
        return self._handle_response(response)

    def update_capa(self, capa_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a CAPA Action."""
        response = requests.put(f"{self.base_url}/api/capa/{capa_id}", json=update_data)
        return self._handle_response(response)

    def get_overdue_capas(self) -> List[Dict[str, Any]]:
        """Get all overdue CAPA actions."""
        response = requests.get(f"{self.base_url}/api/capa/overdue")
        return self._handle_response(response)

    def get_capa_statistics(self) -> Dict[str, Any]:
        """Get CAPA statistics."""
        response = requests.get(f"{self.base_url}/api/capa/statistics")
        return self._handle_response(response)
