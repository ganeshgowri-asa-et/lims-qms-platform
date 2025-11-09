"""
API client utilities for Streamlit frontend
"""
import requests
from typing import Optional, Dict, List
import os

# API Base URL (configurable via environment variable)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


class APIClient:
    """Client for interacting with LIMS/QMS API"""

    @staticmethod
    def _handle_response(response):
        """Handle API response"""
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 204:
            return None
        else:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error: {error_detail}")

    # Customer endpoints
    @staticmethod
    def create_customer(customer_data: dict) -> dict:
        """Create a new customer"""
        response = requests.post(f"{API_BASE_URL}/customers", json=customer_data)
        return APIClient._handle_response(response)

    @staticmethod
    def get_customers(customer_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]:
        """Get list of customers"""
        params = {}
        if customer_type:
            params["customer_type"] = customer_type
        if is_active is not None:
            params["is_active"] = is_active

        response = requests.get(f"{API_BASE_URL}/customers", params=params)
        return APIClient._handle_response(response)

    @staticmethod
    def get_customer(customer_id: int) -> dict:
        """Get customer by ID"""
        response = requests.get(f"{API_BASE_URL}/customers/{customer_id}")
        return APIClient._handle_response(response)

    # Test Request endpoints
    @staticmethod
    def create_test_request(request_data: dict) -> dict:
        """Create a new test request"""
        response = requests.post(f"{API_BASE_URL}/test-requests", json=request_data)
        return APIClient._handle_response(response)

    @staticmethod
    def get_test_requests(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        customer_id: Optional[int] = None
    ) -> List[dict]:
        """Get list of test requests"""
        params = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if customer_id:
            params["customer_id"] = customer_id

        response = requests.get(f"{API_BASE_URL}/test-requests", params=params)
        return APIClient._handle_response(response)

    @staticmethod
    def get_test_request(trq_number: str) -> dict:
        """Get test request by TRQ number"""
        response = requests.get(f"{API_BASE_URL}/test-requests/{trq_number}")
        return APIClient._handle_response(response)

    @staticmethod
    def update_test_request(trq_number: str, update_data: dict) -> dict:
        """Update test request"""
        response = requests.put(f"{API_BASE_URL}/test-requests/{trq_number}", json=update_data)
        return APIClient._handle_response(response)

    @staticmethod
    def submit_test_request(trq_number: str, submitted_by: str) -> dict:
        """Submit test request"""
        response = requests.post(
            f"{API_BASE_URL}/test-requests/{trq_number}/submit",
            params={"submitted_by": submitted_by}
        )
        return APIClient._handle_response(response)

    @staticmethod
    def approve_test_request(trq_number: str, approved_by: str) -> dict:
        """Approve test request"""
        response = requests.post(
            f"{API_BASE_URL}/test-requests/{trq_number}/approve",
            params={"approved_by": approved_by}
        )
        return APIClient._handle_response(response)

    @staticmethod
    def generate_quote(trq_number: str) -> dict:
        """Generate quote for test request"""
        response = requests.post(f"{API_BASE_URL}/test-requests/{trq_number}/generate-quote")
        return APIClient._handle_response(response)

    @staticmethod
    def approve_quote(trq_number: str, approved_by: str) -> dict:
        """Approve quote"""
        response = requests.post(
            f"{API_BASE_URL}/test-requests/{trq_number}/approve-quote",
            params={"approved_by": approved_by}
        )
        return APIClient._handle_response(response)

    # Sample endpoints
    @staticmethod
    def create_sample(sample_data: dict) -> dict:
        """Create a new sample"""
        response = requests.post(f"{API_BASE_URL}/samples", json=sample_data)
        return APIClient._handle_response(response)

    @staticmethod
    def get_samples(
        status: Optional[str] = None,
        test_request_id: Optional[int] = None,
        sample_type: Optional[str] = None
    ) -> List[dict]:
        """Get list of samples"""
        params = {}
        if status:
            params["status"] = status
        if test_request_id:
            params["test_request_id"] = test_request_id
        if sample_type:
            params["sample_type"] = sample_type

        response = requests.get(f"{API_BASE_URL}/samples", params=params)
        return APIClient._handle_response(response)

    @staticmethod
    def get_sample(sample_number: str) -> dict:
        """Get sample by sample number"""
        response = requests.get(f"{API_BASE_URL}/samples/{sample_number}")
        return APIClient._handle_response(response)

    @staticmethod
    def update_sample(sample_number: str, update_data: dict) -> dict:
        """Update sample"""
        response = requests.put(f"{API_BASE_URL}/samples/{sample_number}", json=update_data)
        return APIClient._handle_response(response)

    @staticmethod
    def receive_sample(sample_number: str, received_by: str) -> dict:
        """Mark sample as received"""
        response = requests.post(
            f"{API_BASE_URL}/samples/{sample_number}/receive",
            params={"received_by": received_by}
        )
        return APIClient._handle_response(response)

    @staticmethod
    def start_testing(sample_number: str) -> dict:
        """Start testing on sample"""
        response = requests.post(f"{API_BASE_URL}/samples/{sample_number}/start-testing")
        return APIClient._handle_response(response)

    @staticmethod
    def complete_testing(sample_number: str) -> dict:
        """Complete testing on sample"""
        response = requests.post(f"{API_BASE_URL}/samples/{sample_number}/complete-testing")
        return APIClient._handle_response(response)

    # Health check
    @staticmethod
    def health_check() -> dict:
        """Check API health"""
        response = requests.get(f"{API_BASE_URL}/health")
        return APIClient._handle_response(response)
