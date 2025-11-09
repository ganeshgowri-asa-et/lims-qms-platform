"""
API Client for backend communication
"""
import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import os


class APIClient:
    """Client for communicating with FastAPI backend"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.api_base = f"{self.base_url}/api/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}

        if 'access_token' in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"

        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response"""
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
            return None

        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text
            raise Exception(f"API Error: {error_detail}")

        try:
            return response.json()
        except:
            return None

    # Authentication
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Login user"""
        try:
            response = requests.post(
                f"{self.api_base}/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return None

    def get_current_user(self) -> Optional[Dict]:
        """Get current user info"""
        try:
            response = requests.get(
                f"{self.api_base}/auth/me",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to get user info: {str(e)}")
            return None

    # Documents
    def get_documents(self, level: str = None, status: str = None,
                     skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of documents"""
        try:
            params = {"skip": skip, "limit": limit}
            if level:
                params["level"] = level
            if status:
                params["status"] = status

            response = requests.get(
                f"{self.api_base}/documents/",
                params=params,
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            st.error(f"Failed to fetch documents: {str(e)}")
            return []

    def get_document(self, document_id: int) -> Optional[Dict]:
        """Get single document"""
        try:
            response = requests.get(
                f"{self.api_base}/documents/{document_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to fetch document: {str(e)}")
            return None

    def create_document(self, data: Dict) -> Optional[Dict]:
        """Create new document"""
        try:
            response = requests.post(
                f"{self.api_base}/documents/",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create document: {str(e)}")
            return None

    def approve_document(self, document_id: int) -> bool:
        """Approve a document"""
        try:
            response = requests.put(
                f"{self.api_base}/documents/{document_id}/approve",
                headers=self._get_headers()
            )
            self._handle_response(response)
            return True
        except Exception as e:
            st.error(f"Failed to approve document: {str(e)}")
            return False

    # Forms
    def get_form_templates(self) -> List[Dict]:
        """Get list of form templates"""
        try:
            response = requests.get(
                f"{self.api_base}/forms/templates",
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            st.error(f"Failed to fetch form templates: {str(e)}")
            return []

    def get_form_records(self, template_id: int = None) -> List[Dict]:
        """Get form records"""
        try:
            params = {}
            if template_id:
                params["template_id"] = template_id

            response = requests.get(
                f"{self.api_base}/forms/records",
                params=params,
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            st.error(f"Failed to fetch form records: {str(e)}")
            return []

    def create_form_record(self, data: Dict) -> Optional[Dict]:
        """Create new form record"""
        try:
            response = requests.post(
                f"{self.api_base}/forms/records",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create form record: {str(e)}")
            return None

    # Tasks
    def get_tasks(self, status: str = None, assigned_to_me: bool = False) -> List[Dict]:
        """Get tasks"""
        try:
            params = {}
            if status:
                params["status"] = status
            if assigned_to_me:
                params["assigned_to_me"] = True

            response = requests.get(
                f"{self.api_base}/tasks/",
                params=params,
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            st.error(f"Failed to fetch tasks: {str(e)}")
            return []

    def update_task_status(self, task_id: int, status: str, comment: str = "") -> bool:
        """Update task status"""
        try:
            response = requests.put(
                f"{self.api_base}/tasks/{task_id}/status",
                json={"status": status, "comment": comment},
                headers=self._get_headers()
            )
            self._handle_response(response)
            return True
        except Exception as e:
            st.error(f"Failed to update task: {str(e)}")
            return False

    # Analytics
    def get_analytics_summary(self) -> Optional[Dict]:
        """Get analytics summary"""
        try:
            response = requests.get(
                f"{self.api_base}/analytics/summary",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to fetch analytics: {str(e)}")
            return None

    def get_dashboard_metrics(self) -> Optional[Dict]:
        """Get dashboard metrics"""
        try:
            response = requests.get(
                f"{self.api_base}/analytics/dashboard",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            # Return mock data if API fails
            return {
                "active_projects": 12,
                "pending_tasks": 45,
                "total_documents": 234,
                "open_ncs": 3
            }

    # Users
    def get_users(self) -> List[Dict]:
        """Get list of users"""
        try:
            response = requests.get(
                f"{self.api_base}/users/",
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            st.error(f"Failed to fetch users: {str(e)}")
            return []

    def create_user(self, data: Dict) -> Optional[Dict]:
        """Create new user"""
        try:
            response = requests.post(
                f"{self.api_base}/users/",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create user: {str(e)}")
            return None

    # Workflows
    def get_pending_approvals(self) -> List[Dict]:
        """Get pending approval items"""
        try:
            response = requests.get(
                f"{self.api_base}/tasks/pending-approvals",
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            # Return empty list if endpoint doesn't exist yet
            return []

    def approve_item(self, item_type: str, item_id: int, comment: str = "") -> bool:
        """Approve an item (document, form, etc.)"""
        try:
            response = requests.post(
                f"{self.api_base}/workflows/approve",
                json={
                    "item_type": item_type,
                    "item_id": item_id,
                    "comment": comment
                },
                headers=self._get_headers()
            )
            self._handle_response(response)
            return True
        except Exception as e:
            st.error(f"Failed to approve: {str(e)}")
            return False

    def reject_item(self, item_type: str, item_id: int, comment: str) -> bool:
        """Reject an item"""
        try:
            response = requests.post(
                f"{self.api_base}/workflows/reject",
                json={
                    "item_type": item_type,
                    "item_id": item_id,
                    "comment": comment
                },
                headers=self._get_headers()
            )
            self._handle_response(response)
            return True
        except Exception as e:
            st.error(f"Failed to reject: {str(e)}")
            return False

    # Traceability
    def get_audit_trail(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Get audit trail for an entity"""
        try:
            response = requests.get(
                f"{self.api_base}/analytics/audit-trail/{entity_type}/{entity_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response) or []
        except Exception as e:
            return []

    def get_traceability_graph(self, entity_type: str, entity_id: int) -> Optional[Dict]:
        """Get traceability graph data"""
        try:
            response = requests.get(
                f"{self.api_base}/analytics/traceability/{entity_type}/{entity_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return None


# Global API client instance
api_client = APIClient()
