"""
Document & Template Management - Example Usage Scripts
Demonstrates common use cases and workflows
"""
import requests
from typing import Dict, Any
import json
from datetime import date

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Get token by logging in first
TOKEN = "your_jwt_token_here"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


class DocumentManagementClient:
    """Client for interacting with Document Management API"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    # ==================== Authentication ====================

    @staticmethod
    def login(username: str, password: str) -> str:
        """Login and get JWT token"""
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        return response.json()["access_token"]

    # ==================== Document Operations ====================

    def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        response = requests.post(
            f"{self.base_url}/documents/",
            json=document_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_document(self, document_id: int) -> Dict[str, Any]:
        """Get document details"""
        response = requests.get(
            f"{self.base_url}/documents/{document_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_documents(self, **filters) -> list:
        """List documents with filters"""
        response = requests.get(
            f"{self.base_url}/documents/",
            params=filters,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def search_documents(self, query: str) -> list:
        """Search documents"""
        return self.list_documents(search=query)

    # ==================== Lifecycle Operations ====================

    def submit_for_review(self, document_id: int, checker_id: int) -> Dict[str, Any]:
        """Submit document for review"""
        response = requests.put(
            f"{self.base_url}/documents/{document_id}/submit-review",
            json={"checker_id": checker_id},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def approve_document(self, document_id: int, effective_date: str = None) -> Dict[str, Any]:
        """Approve document"""
        data = {"effective_date": effective_date} if effective_date else {}
        response = requests.put(
            f"{self.base_url}/documents/{document_id}/approve",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # ==================== Version Control ====================

    def create_version(self, document_id: int, file_path: str, change_summary: str,
                       change_type: str = "Minor") -> Dict[str, Any]:
        """Create new document version"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'change_summary': change_summary,
                'change_type': change_type
            }
            response = requests.post(
                f"{self.base_url}/documents/{document_id}/versions",
                files=files,
                data=data,
                headers={"Authorization": self.headers["Authorization"]}
            )
            response.raise_for_status()
            return response.json()

    def get_versions(self, document_id: int) -> list:
        """Get all versions of a document"""
        response = requests.get(
            f"{self.base_url}/documents/{document_id}/versions",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # ==================== Linking & Traceability ====================

    def link_documents(self, parent_id: int, child_id: int, link_type: str = "references",
                       **kwargs) -> Dict[str, Any]:
        """Link two documents"""
        link_data = {
            "parent_document_id": parent_id,
            "child_document_id": child_id,
            "link_type": link_type,
            **kwargs
        }
        response = requests.post(
            f"{self.base_url}/documents/links",
            json=link_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_hierarchy(self, document_id: int, direction: str = "both") -> Dict[str, Any]:
        """Get document hierarchy"""
        response = requests.get(
            f"{self.base_url}/documents/{document_id}/hierarchy",
            params={"direction": direction},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # ==================== Metadata Operations ====================

    def add_toc_entry(self, document_id: int, toc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add table of contents entry"""
        response = requests.post(
            f"{self.base_url}/documents/{document_id}/toc",
            json=toc_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def add_responsibility(self, document_id: int, responsibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add responsibility (RACI) entry"""
        response = requests.post(
            f"{self.base_url}/documents/{document_id}/responsibilities",
            json=responsibility_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def add_equipment(self, document_id: int, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add equipment entry"""
        response = requests.post(
            f"{self.base_url}/documents/{document_id}/equipment",
            json=equipment_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def add_kpi(self, document_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add KPI entry"""
        response = requests.post(
            f"{self.base_url}/documents/{document_id}/kpis",
            json=kpi_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    # ==================== Template Operations ====================

    def index_template(self, document_id: int, category_name: str, tags: list,
                       keywords: list, metadata: dict = None) -> Dict[str, Any]:
        """Index document as template"""
        index_data = {
            "category_name": category_name,
            "tags": tags,
            "keywords": keywords,
            "metadata": metadata or {}
        }
        response = requests.post(
            f"{self.base_url}/documents/{document_id}/index-template",
            json=index_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def search_templates(self, **filters) -> list:
        """Search templates"""
        # Convert tags list to comma-separated string if provided
        if 'tags' in filters and isinstance(filters['tags'], list):
            filters['tags'] = ','.join(filters['tags'])

        response = requests.get(
            f"{self.base_url}/documents/templates/search",
            params=filters,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# ==================== EXAMPLE WORKFLOWS ====================

def example_1_create_quality_manual():
    """Example 1: Create a Quality Manual (Level 1 Document)"""
    print("\n=== Example 1: Create Quality Manual ===\n")

    # Get token (replace with actual login)
    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Create Level 1 document
    quality_manual = client.create_document({
        "title": "Quality Management System Manual",
        "level": "Level 1",
        "document_type": "Quality Manual",
        "iso_standard": "ISO/IEC 17025",
        "description": "Main quality management system manual for the organization",
        "purpose": "To establish the quality management system framework",
        "scope": "Applies to all testing and calibration activities",
        "department": "Quality",
        "review_frequency_months": 12,
        "retention_policy": "Permanent",
        "tags": ["quality", "iso17025", "qms"],
        "keywords": ["quality", "management", "system", "manual"]
    })

    print(f"Created Quality Manual: {quality_manual['document_number']}")
    print(f"Document ID: {quality_manual['id']}")

    # Add Table of Contents
    toc_entries = [
        {"section_number": "1", "section_title": "Scope and Applicability", "level": 1},
        {"section_number": "2", "section_title": "Normative References", "level": 1},
        {"section_number": "3", "section_title": "Terms and Definitions", "level": 1},
        {"section_number": "4", "section_title": "Organization Structure", "level": 1},
        {"section_number": "4.1", "section_title": "Leadership and Commitment", "level": 2},
        {"section_number": "4.2", "section_title": "Quality Policy", "level": 2},
    ]

    for toc in toc_entries:
        client.add_toc_entry(quality_manual['id'], toc)

    print(f"Added {len(toc_entries)} TOC entries")

    # Add responsibilities
    client.add_responsibility(quality_manual['id'], {
        "role_title": "Quality Manager",
        "is_accountable": True,
        "department": "Quality",
        "tasks": ["Maintain QMS", "Conduct management review", "Ensure compliance"]
    })

    print("Added responsibilities")
    return quality_manual


def example_2_create_test_procedure_with_hierarchy():
    """Example 2: Create Test Procedure with Full Hierarchy"""
    print("\n=== Example 2: Create Test Procedure with Hierarchy ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Create Level 3 Test Procedure
    test_procedure = client.create_document({
        "title": "IEC 61215 Thermal Cycling Test Procedure",
        "level": "Level 3",
        "document_type": "Procedure",
        "pv_standard": "IEC 61215",
        "description": "Procedure for performing thermal cycling tests on PV modules",
        "department": "Testing",
        "review_frequency_months": 24,
        "tags": ["iec61215", "thermal-cycling", "pv-testing"],
        "keywords": ["thermal", "cycling", "temperature", "pv", "module"]
    })

    print(f"Created Test Procedure: {test_procedure['document_number']}")

    # Add equipment
    equipment_list = [
        {
            "name": "Thermal Cycling Chamber",
            "equipment_type": "Equipment",
            "model": "TC-2000X",
            "manufacturer": "Climate Test Inc.",
            "specifications": "Temperature range: -40°C to +85°C, Humidity control",
            "calibration_required": True
        },
        {
            "name": "Temperature Data Logger",
            "equipment_type": "Equipment",
            "model": "DL-500",
            "manufacturer": "Data Systems Inc.",
            "calibration_required": True
        }
    ]

    for equipment in equipment_list:
        client.add_equipment(test_procedure['id'], equipment)

    print(f"Added {len(equipment_list)} equipment items")

    # Add KPIs
    client.add_kpi(test_procedure['id'], {
        "name": "Test Completion Time",
        "metric": "Time to complete 200 thermal cycles",
        "unit_of_measure": "hours",
        "target_value": 200,
        "measurement_frequency": "Per Test"
    })

    # Link to Level 2 procedure (if exists)
    # Assuming quality_procedure_id = 10
    quality_procedure_id = 10
    client.link_documents(
        parent_id=quality_procedure_id,
        child_id=test_procedure['id'],
        link_type="implements",
        description="Test procedure implements quality system requirements",
        section_reference="Section 7.2",
        compliance_reference="ISO/IEC 17025:2017, 7.2.1"
    )

    print("Linked to parent quality procedure")

    return test_procedure


def example_3_create_and_index_template():
    """Example 3: Create Template and Index It"""
    print("\n=== Example 3: Create and Index Template ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Create Level 4 Template
    template = client.create_document({
        "title": "Calibration Record Form",
        "level": "Level 4",
        "document_type": "Form",
        "iso_standard": "ISO/IEC 17025",
        "description": "Standard form for recording equipment calibration results",
        "department": "Quality",
        "tags": ["calibration", "equipment", "quality"],
        "keywords": ["calibration", "record", "equipment", "verification"]
    })

    print(f"Created Template: {template['document_number']}")

    # Index as template
    indexed = client.index_template(
        document_id=template['id'],
        category_name="Calibration Forms",
        tags=["calibration", "equipment", "iso17025"],
        keywords=["calibration", "equipment", "verification", "measurement"],
        metadata={
            "template_type": "form",
            "format": "fillable_pdf",
            "fields_count": 25
        }
    )

    print(f"Indexed template in category: Calibration Forms")

    # Search for templates
    results = client.search_templates(
        query="calibration",
        tags=["equipment", "calibration"]
    )

    print(f"Found {len(results)} matching templates")

    return template


def example_4_version_control_workflow():
    """Example 4: Complete Version Control Workflow"""
    print("\n=== Example 4: Version Control Workflow ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Assume we have a document with ID 1
    document_id = 1

    # Create version 1.0 (initial version created with file upload)
    # This would be done via file upload in real scenario
    print("Initial version created during document creation")

    # Get current versions
    versions = client.get_versions(document_id)
    print(f"Current versions: {len(versions)}")

    # Submit for review
    client.submit_for_review(document_id, checker_id=5)
    print("Submitted for review")

    # Approve document
    client.approve_document(document_id, effective_date="2025-02-01")
    print("Document approved")

    # Later, create a new version with changes
    # (In real scenario, this would upload a new file)
    # client.create_version(
    #     document_id=document_id,
    #     file_path="/path/to/updated/document.pdf",
    #     change_summary="Updated calibration frequency from annual to semi-annual",
    #     change_type="Major"
    # )

    print("New version would be created with file upload")


def example_5_bulk_template_indexing():
    """Example 5: Bulk Index 47 Templates"""
    print("\n=== Example 5: Bulk Template Indexing ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Assume we have 47 Level 4 documents already created
    # IDs from 100 to 146
    templates_to_index = []

    # Template categories and their documents
    template_mapping = {
        "Quality Management Forms": list(range(100, 110)),
        "Test Protocols": list(range(110, 120)),
        "Calibration Forms": list(range(120, 130)),
        "Inspection Checklists": list(range(130, 140)),
        "Equipment Forms": list(range(140, 147))
    }

    for category, doc_ids in template_mapping.items():
        for doc_id in doc_ids:
            templates_to_index.append({
                "document_id": doc_id,
                "category": category,
                "tags": [category.lower().replace(" ", "-"), "template"],
                "keywords": [category, "form", "template"]
            })

    # Bulk index
    response = requests.post(
        f"{BASE_URL}/documents/templates/bulk-index",
        json={"templates": templates_to_index},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )

    result = response.json()
    print(f"Successfully indexed: {result['success']}/{result['total']} templates")


def example_6_document_traceability_report():
    """Example 6: Generate Document Traceability Report"""
    print("\n=== Example 6: Document Traceability Report ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Get hierarchy for a Level 3 document
    document_id = 25

    hierarchy = client.get_hierarchy(document_id, direction="both")

    print(f"Document ID: {hierarchy['document_id']}")
    print(f"\nParent Documents (implements/derives from):")
    for parent in hierarchy['parent_documents']:
        print(f"  - {parent['document_number']}: {parent['title']}")
        print(f"    Level: {parent['level']}, Link: {parent['link_type']}")

    print(f"\nChild Documents (used by):")
    for child in hierarchy['child_documents']:
        print(f"  - {child['document_number']}: {child['title']}")
        print(f"    Level: {child['level']}, Link: {child['link_type']}")


def example_7_search_and_filter():
    """Example 7: Advanced Search and Filtering"""
    print("\n=== Example 7: Advanced Search and Filtering ===\n")

    token = "your_token_here"
    client = DocumentManagementClient(BASE_URL, token)

    # Search by ISO standard
    iso_docs = client.list_documents(
        iso_standard="ISO/IEC 17025",
        status="Approved"
    )
    print(f"Found {len(iso_docs)} approved ISO 17025 documents")

    # Search by level and type
    templates = client.list_documents(
        level="Level 4",
        document_type="Template",
        is_template=True
    )
    print(f"Found {len(templates)} Level 4 templates")

    # Text search
    search_results = client.search_documents("calibration")
    print(f"Found {len(search_results)} documents matching 'calibration'")

    # Template-specific search
    pv_templates = client.search_templates(
        query="pv module",
        tags=["iec61215", "testing"]
    )
    print(f"Found {len(pv_templates)} PV module test templates")


if __name__ == "__main__":
    print("=" * 60)
    print("Document & Template Management - Example Usage")
    print("=" * 60)

    print("\nNOTE: Replace 'your_token_here' with actual JWT token from login")
    print("To get token: token = DocumentManagementClient.login('username', 'password')")

    print("\n\nAvailable Examples:")
    print("1. Create Quality Manual (Level 1)")
    print("2. Create Test Procedure with Hierarchy (Level 3)")
    print("3. Create and Index Template (Level 4)")
    print("4. Version Control Workflow")
    print("5. Bulk Template Indexing (47 templates)")
    print("6. Document Traceability Report")
    print("7. Advanced Search and Filtering")

    print("\n\nTo run examples, uncomment the function calls below:")
    # example_1_create_quality_manual()
    # example_2_create_test_procedure_with_hierarchy()
    # example_3_create_and_index_template()
    # example_4_version_control_workflow()
    # example_5_bulk_template_indexing()
    # example_6_document_traceability_report()
    # example_7_search_and_filter()
