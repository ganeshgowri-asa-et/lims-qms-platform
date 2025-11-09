"""
Data Capture Engine - Usage Examples
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

class DataCaptureExample:
    def __init__(self):
        self.token = None
        self.headers = {}

    def login(self):
        """Login and get JWT token"""
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": USERNAME, "password": PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✓ Logged in successfully")
            return True
        else:
            print("✗ Login failed:", response.text)
            return False

    def example_1_create_simple_record(self):
        """Example 1: Create a simple form record"""
        print("\n=== Example 1: Create Simple Record ===")

        record_data = {
            "template_id": 1,
            "title": "Daily Temperature Log",
            "values": {
                "date": datetime.now().isoformat(),
                "location": "Lab A",
                "temperature": 23.5,
                "humidity": 45,
                "recorded_by": "John Doe"
            },
            "auto_submit": False
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records",
            json=record_data,
            headers=self.headers
        )

        if response.status_code == 201:
            record = response.json()
            print(f"✓ Record created: {record['record_number']}")
            print(f"  Status: {record['status']}")
            print(f"  Completion: {record['completion_percentage']}%")
            return record["id"]
        else:
            print("✗ Failed:", response.text)
            return None

    def example_2_validate_before_submit(self):
        """Example 2: Validate data before submission"""
        print("\n=== Example 2: Validate Before Submit ===")

        validation_data = {
            "template_id": 1,
            "values": {
                "temperature": 23.5,
                "humidity": 45
            }
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/validate",
            json=validation_data,
            headers=self.headers
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Validation result:")
            print(f"  Is valid: {result['is_valid']}")
            print(f"  Errors: {len(result['errors'])}")
            print(f"  Warnings: {len(result['warnings'])}")
            print(f"  Completion: {result['completion_percentage']}%")
            print(f"  Validation score: {result['validation_score']}")

            if result['errors']:
                print("\n  Errors:")
                for error in result['errors']:
                    print(f"    - {error['field']}: {error['message']}")
        else:
            print("✗ Failed:", response.text)

    def example_3_complete_workflow(self):
        """Example 3: Complete Doer-Checker-Approver workflow"""
        print("\n=== Example 3: Complete Workflow ===")

        # Step 1: Create record
        record_data = {
            "template_id": 1,
            "title": "Quality Inspection Report",
            "values": {
                "date": datetime.now().isoformat(),
                "product_id": "PROD-001",
                "batch_number": "BATCH-2025-001",
                "inspection_result": "Pass",
                "defects_found": 0,
                "inspector_name": "Jane Smith"
            }
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records",
            json=record_data,
            headers=self.headers
        )

        if response.status_code != 201:
            print("✗ Failed to create record")
            return

        record = response.json()
        record_id = record["id"]
        print(f"✓ Record created: {record['record_number']}")

        # Step 2: Submit for review
        response = requests.post(
            f"{BASE_URL}/data-capture/records/{record_id}/submit",
            json={"comments": "Ready for quality review"},
            headers=self.headers
        )

        if response.status_code == 200:
            print("✓ Record submitted for review")
        else:
            print("✗ Submit failed:", response.text)
            return

        # Step 3: Checker reviews (in real scenario, this would be a different user)
        response = requests.post(
            f"{BASE_URL}/data-capture/records/{record_id}/review",
            json={
                "action": "approve",
                "comments": "Inspection data verified, ready for final approval"
            },
            headers=self.headers
        )

        if response.status_code == 200:
            print("✓ Checker approved")
        else:
            print("✗ Review failed:", response.text)
            return

        # Step 4: Approver approves
        response = requests.post(
            f"{BASE_URL}/data-capture/records/{record_id}/approve",
            json={
                "action": "approve",
                "comments": "Quality inspection report approved"
            },
            headers=self.headers
        )

        if response.status_code == 200:
            print("✓ Approver approved - Record complete!")
        else:
            print("✗ Approval failed:", response.text)
            return

        # Step 5: Get workflow history
        response = requests.get(
            f"{BASE_URL}/data-capture/records/{record_id}/history",
            headers=self.headers
        )

        if response.status_code == 200:
            history = response.json()
            print(f"\n✓ Workflow history ({len(history)} events):")
            for event in history:
                print(f"  - {event['action']}: {event['from_status']} → {event['to_status']}")
                print(f"    By: {event['actor']['full_name']}")
                print(f"    At: {event['timestamp']}")

    def example_4_auto_save_draft(self):
        """Example 4: Auto-save draft functionality"""
        print("\n=== Example 4: Auto-save Draft ===")

        # Save draft
        draft_data = {
            "template_id": 1,
            "values": {
                "temperature": 22.0,
                "humidity": 50,
                "notes": "Work in progress..."
            }
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/drafts",
            json=draft_data,
            headers=self.headers
        )

        if response.status_code == 200:
            draft = response.json()
            print(f"✓ Draft saved at: {draft['last_saved_at']}")

            # Retrieve draft
            response = requests.get(
                f"{BASE_URL}/data-capture/drafts/1",
                headers=self.headers
            )

            if response.status_code == 200:
                retrieved = response.json()
                print(f"✓ Draft retrieved: {retrieved['draft_data']}")
        else:
            print("✗ Failed:", response.text)

    def example_5_bulk_upload(self):
        """Example 5: Bulk upload from CSV"""
        print("\n=== Example 5: Bulk Upload ===")

        # First, download the template
        response = requests.get(
            f"{BASE_URL}/data-capture/templates/1/bulk-template",
            headers=self.headers
        )

        if response.status_code == 200:
            with open("/tmp/bulk_template.csv", "wb") as f:
                f.write(response.content)
            print("✓ Template downloaded to /tmp/bulk_template.csv")
            print("\n  Fill in the template and upload using:")
            print("  files = {'file': open('filled_template.csv', 'rb')}")
            print("  requests.post(f'{BASE_URL}/data-capture/bulk-upload/1', files=files, headers=headers)")
        else:
            print("✗ Failed to download template")

    def example_6_digital_signature(self):
        """Example 6: Capture digital signature"""
        print("\n=== Example 6: Digital Signature ===")

        # Create a record first
        record_data = {
            "template_id": 1,
            "title": "Signed Document",
            "values": {"test": "data"}
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records",
            json=record_data,
            headers=self.headers
        )

        if response.status_code != 201:
            print("✗ Failed to create record")
            return

        record_id = response.json()["id"]

        # Capture signature (using base64 encoded image data)
        signature_data = {
            "signature_type": "doer",
            "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "signature_method": "drawn",
            "ip_address": "192.168.1.1"
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records/{record_id}/signatures",
            json=signature_data,
            headers=self.headers
        )

        if response.status_code == 201:
            print("✓ Signature captured")

            # Get signature report
            response = requests.get(
                f"{BASE_URL}/data-capture/records/{record_id}/signature-report",
                headers=self.headers
            )

            if response.status_code == 200:
                report = response.json()
                print(f"\nSignature Report:")
                print(f"  Total signatures: {report['signature_count']}")
                print(f"  Valid signatures: {report['valid_signature_count']}")
                print(f"  Signature complete: {report['signature_complete']}")
                print(f"  Missing: {report['missing_signatures']}")
        else:
            print("✗ Failed:", response.text)

    def example_7_comments_and_collaboration(self):
        """Example 7: Add comments for collaboration"""
        print("\n=== Example 7: Comments & Collaboration ===")

        # Create a record
        record_data = {
            "template_id": 1,
            "title": "Collaborative Review",
            "values": {"test": "data"}
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records",
            json=record_data,
            headers=self.headers
        )

        if response.status_code != 201:
            print("✗ Failed to create record")
            return

        record_id = response.json()["id"]

        # Add comment
        comment_data = {
            "content": "Please verify the temperature readings",
            "comment_type": "clarification"
        }

        response = requests.post(
            f"{BASE_URL}/data-capture/records/{record_id}/comments",
            json=comment_data,
            headers=self.headers
        )

        if response.status_code == 201:
            print("✓ Comment added")

            # Get all comments
            response = requests.get(
                f"{BASE_URL}/data-capture/records/{record_id}/comments",
                headers=self.headers
            )

            if response.status_code == 200:
                comments = response.json()
                print(f"\nComments ({len(comments)}):")
                for comment in comments:
                    print(f"  - {comment['user']['full_name']}: {comment['content']}")
                    print(f"    Type: {comment['comment_type']}")
                    print(f"    Resolved: {comment['is_resolved']}")
        else:
            print("✗ Failed:", response.text)

    def example_8_notifications(self):
        """Example 8: Get notifications"""
        print("\n=== Example 8: Notifications ===")

        # Get unread count
        response = requests.get(
            f"{BASE_URL}/data-capture/notifications/unread-count",
            headers=self.headers
        )

        if response.status_code == 200:
            count = response.json()["count"]
            print(f"✓ Unread notifications: {count}")

        # Get all notifications
        response = requests.get(
            f"{BASE_URL}/data-capture/notifications?limit=10",
            headers=self.headers
        )

        if response.status_code == 200:
            notifications = response.json()
            print(f"\nRecent notifications ({len(notifications)}):")
            for notif in notifications[:5]:  # Show first 5
                print(f"  - [{notif['category']}] {notif['title']}")
                print(f"    {notif['message']}")
                print(f"    Read: {notif['is_read']}")
        else:
            print("✗ Failed:", response.text)

    def run_all_examples(self):
        """Run all examples"""
        if not self.login():
            return

        print("\n" + "="*60)
        print("DATA CAPTURE ENGINE - USAGE EXAMPLES")
        print("="*60)

        self.example_1_create_simple_record()
        self.example_2_validate_before_submit()
        self.example_3_complete_workflow()
        self.example_4_auto_save_draft()
        self.example_5_bulk_upload()
        self.example_6_digital_signature()
        self.example_7_comments_and_collaboration()
        self.example_8_notifications()

        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)


if __name__ == "__main__":
    examples = DataCaptureExample()
    examples.run_all_examples()
