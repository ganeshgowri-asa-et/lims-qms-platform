# Traceability & Audit Trail Engine

## Overview

The Traceability & Audit Trail Engine provides comprehensive end-to-end traceability for the LIMS-QMS platform, ensuring full compliance with ISO 17025, ISO 9001, and other quality management standards.

## Features

### 1. Document Lineage & Traceability

#### Forward Traceability
Trace downstream dependencies from high-level policies to detailed records:
- **Level 1 (Policy)** → Level 2 (Procedures) → Level 3 (Work Instructions) → Level 4 (Forms) → Level 5 (Records)

**API Endpoint:**
```http
GET /api/v1/traceability/forward/{entity_type}/{entity_id}?max_depth=10
```

**Example Response:**
```json
{
  "entity_type": "document",
  "entity_id": 1,
  "entity_details": {
    "name": "Quality Policy",
    "status": "approved"
  },
  "depth": 0,
  "downstream": [
    {
      "entity_type": "document",
      "entity_id": 5,
      "link_type": "child",
      "depth": 1,
      "downstream": [...]
    }
  ],
  "total_dependencies": 15
}
```

#### Backward Traceability
Trace upstream sources from records back to originating policies:
- **Level 5 (Records)** → Level 4 (Forms) → Level 3 (Work Instructions) → Level 2 (Procedures) → Level 1 (Policy)

**API Endpoint:**
```http
GET /api/v1/traceability/backward/{entity_type}/{entity_id}?max_depth=10
```

#### Bi-directional Navigation
Get both upstream and downstream links for easy navigation:

**API Endpoint:**
```http
GET /api/v1/traceability/bidirectional/{entity_type}/{entity_id}
```

#### Impact Analysis
Analyze the impact of changing a document:

**API Endpoint:**
```http
POST /api/v1/traceability/impact-analysis
```

**Request Body:**
```json
{
  "entity_type": "document",
  "entity_id": 1,
  "change_description": "Updating test procedure to new version"
}
```

**Response:**
```json
{
  "impact_scope": "high",
  "total_affected": 23,
  "affected_entities": [
    {"entity_type": "form_record", "entity_id": 10, "depth": 2},
    {"entity_type": "task", "entity_id": 50, "depth": 3}
  ]
}
```

### 2. Data Lineage (Medallion Architecture)

Track data transformations through pipeline stages:
- **Bronze** (Raw Data) → **Silver** (Processed Data) → **Gold** (Final Data)

#### Track Data Transformation

**API Endpoint:**
```http
POST /api/v1/traceability/data-lineage
```

**Request Body:**
```json
{
  "source_entity_type": "test_result",
  "source_entity_id": 100,
  "source_stage": "bronze",
  "target_entity_type": "test_result",
  "target_entity_id": 101,
  "target_stage": "silver",
  "transformation_type": "cleaning",
  "transformation_logic": "Remove outliers using 3-sigma rule",
  "equipment_id": 5,
  "software_version": "DataClean v2.1",
  "data_quality_score": 95.5,
  "validation_status": "passed"
}
```

#### Get Data Lineage Path

**API Endpoint:**
```http
GET /api/v1/traceability/data-lineage/{entity_type}/{entity_id}
```

**Response:**
```json
{
  "lineage_path": [
    {
      "source": {"entity_type": "test_result", "entity_id": 100, "stage": "bronze"},
      "target": {"entity_type": "test_result", "entity_id": 101, "stage": "silver"},
      "transformation_type": "cleaning",
      "equipment_id": 5,
      "data_quality_score": 95.5
    }
  ],
  "total_stages": 3
}
```

### 3. Requirements Traceability Matrix (RTM)

Link requirements to evidence and track verification status.

#### Create Requirement

**API Endpoint:**
```http
POST /api/v1/traceability/requirements
```

**Request Body:**
```json
{
  "requirement_number": "REQ-ISO17025-001",
  "requirement_title": "Equipment Calibration Records",
  "requirement_description": "All test equipment must be calibrated annually",
  "requirement_source": "ISO 17025:2017 6.4.6",
  "requirement_category": "Equipment",
  "requirement_priority": "critical",
  "compliance_standards": ["ISO 17025", "ISO 9001"]
}
```

#### Link Requirement to Evidence

**API Endpoint:**
```http
POST /api/v1/traceability/requirements/link
```

**Request Body:**
```json
{
  "requirement_id": 1,
  "entity_type": "calibration",
  "entity_id": 25,
  "verification_method": "inspection"
}
```

#### Get RTM Coverage Report

**API Endpoint:**
```http
GET /api/v1/traceability/requirements/coverage
```

**Response:**
```json
{
  "summary": {
    "total_requirements": 50,
    "verified": 45,
    "partially_verified": 3,
    "not_verified": 2,
    "coverage_percentage": 90.0
  },
  "by_category": {
    "Equipment": [...],
    "Personnel": [...]
  },
  "gaps": [
    {
      "requirement_number": "REQ-ISO17025-042",
      "title": "Training Matrix",
      "priority": "high"
    }
  ]
}
```

### 4. Audit Trail (Immutable, Event-Sourced)

Complete change history with blockchain-inspired immutability.

#### Audit Log Fields
- **Who**: User ID, name, role
- **What**: Action, field changed, old/new values
- **When**: Timestamp (UTC + local)
- **Where**: IP address, location, device
- **Why**: Reason for change (mandatory comment)

#### Get Entity Audit History

**API Endpoint:**
```http
GET /api/v1/traceability/audit-logs/{entity_type}/{entity_id}?limit=100
```

**Response:**
```json
[
  {
    "event_sequence": 12345,
    "user_id": 10,
    "action": "update",
    "timestamp": "2025-11-09T10:30:00Z",
    "description": "Updated document status",
    "old_values": {"status": "draft"},
    "new_values": {"status": "approved"},
    "ip_address": "192.168.1.100",
    "location": "Lab 1, Building A",
    "reason": "Document approved after review",
    "checksum": "a3b5c7d9...",
    "previous_checksum": "f8e6d4c2..."
  }
]
```

#### Search Audit Logs

**API Endpoint:**
```http
POST /api/v1/traceability/audit-logs/search
```

**Request Body:**
```json
{
  "user_id": 10,
  "entity_type": "document",
  "action": "update",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-11-09T23:59:59Z",
  "limit": 100,
  "offset": 0
}
```

#### Verify Audit Chain Integrity

**API Endpoint:**
```http
GET /api/v1/traceability/audit-logs/verify-integrity?start_sequence=1&end_sequence=10000
```

**Response:**
```json
{
  "total_events_checked": 10000,
  "integrity_intact": true,
  "issues_found": 0,
  "issues": []
}
```

#### Export Audit Logs

**API Endpoint:**
```http
POST /api/v1/traceability/audit-logs/export?format=json
```

#### Reconstruct Entity State (Event Sourcing)

**API Endpoint:**
```http
GET /api/v1/traceability/audit-logs/reconstruct/{entity_type}/{entity_id}?at_timestamp=2025-01-15T12:00:00Z
```

### 5. Version Comparison

Create snapshots and compare different versions of entities.

#### Create Snapshot

**API Endpoint:**
```http
POST /api/v1/traceability/snapshots
```

**Request Body:**
```json
{
  "entity_type": "document",
  "entity_id": 1,
  "snapshot_data": {
    "title": "Quality Manual",
    "version": "2.0",
    "content": "..."
  },
  "snapshot_trigger": "approval",
  "notes": "Snapshot created on approval"
}
```

#### Compare Versions

**API Endpoint:**
```http
POST /api/v1/traceability/snapshots/compare
```

**Request Body:**
```json
{
  "entity_type": "document",
  "entity_id": 1,
  "version1": 1,
  "version2": 2
}
```

**Response:**
```json
{
  "version1": {
    "version_number": 1,
    "created_at": "2025-01-01T10:00:00Z",
    "data": {"title": "Quality Manual", "version": "1.0"}
  },
  "version2": {
    "version_number": 2,
    "created_at": "2025-06-01T10:00:00Z",
    "data": {"title": "Quality Manual", "version": "2.0"}
  },
  "diff": {
    "added": {},
    "removed": {},
    "modified": {
      "version": {"old": "1.0", "new": "2.0"}
    }
  }
}
```

### 6. Chain of Custody

Track sample and equipment movement with full custody records.

#### Record Custody Event

**API Endpoint:**
```http
POST /api/v1/traceability/chain-of-custody
```

**Request Body:**
```json
{
  "entity_type": "sample",
  "entity_id": 100,
  "entity_identifier": "SAMPLE-2025-001",
  "event_type": "transferred",
  "from_user_id": 10,
  "to_user_id": 15,
  "from_location": "Lab 1",
  "to_location": "Lab 2",
  "condition_before": "sealed, 4°C",
  "condition_after": "sealed, 4°C",
  "seal_number": "SEAL-12345",
  "notes": "Transfer for testing"
}
```

#### Get Custody Chain

**API Endpoint:**
```http
GET /api/v1/traceability/chain-of-custody/{entity_type}/{entity_id}
```

**Response:**
```json
[
  {
    "event_id": 1,
    "event_type": "received",
    "timestamp": "2025-11-01T08:00:00Z",
    "from_user_id": null,
    "to_user_id": 10,
    "to_location": "Lab 1",
    "condition_after": "sealed, 4°C",
    "integrity_check": true
  },
  {
    "event_id": 2,
    "event_type": "transferred",
    "timestamp": "2025-11-05T10:30:00Z",
    "from_user_id": 10,
    "to_user_id": 15,
    "from_location": "Lab 1",
    "to_location": "Lab 2",
    "integrity_check": true
  }
]
```

### 7. Compliance Reports

Generate audit-ready reports for ISO 17025/9001 compliance.

#### Create Compliance Evidence

**API Endpoint:**
```http
POST /api/v1/traceability/compliance-evidence
```

**Request Body:**
```json
{
  "evidence_number": "EVID-2025-001",
  "evidence_type": "calibration",
  "title": "Equipment Calibration Certificate",
  "description": "Annual calibration of pH meter",
  "compliance_standards": ["ISO 17025", "ISO 9001"],
  "evidence_date": "2025-11-01T00:00:00Z",
  "expiry_date": "2026-11-01T00:00:00Z",
  "entity_type": "calibration",
  "entity_id": 25,
  "document_references": [100, 101]
}
```

#### Generate Compliance Report

**API Endpoint:**
```http
POST /api/v1/traceability/compliance-reports
```

**Request Body:**
```json
{
  "standards": ["ISO 17025", "ISO 9001"],
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "report_generated": "2025-11-09T10:00:00Z",
  "summary": {
    "total_evidence": 150,
    "valid": 140,
    "expired": 8,
    "superseded": 2
  },
  "by_type": {
    "calibration": [...],
    "training": [...],
    "audit": [...]
  },
  "by_standard": {
    "ISO 17025": ["EVID-001", "EVID-002", ...],
    "ISO 9001": ["EVID-050", "EVID-051", ...]
  }
}
```

## Technical Architecture

### Event Sourcing Pattern
- All changes are captured as immutable events
- Entity state can be reconstructed from event history
- Supports time-travel queries

### Blockchain-Inspired Immutability
- Each audit event contains:
  - SHA-256 checksum of event data
  - Link to previous event's checksum
  - Sequential event number
- Chain integrity can be verified at any time

### Automatic Audit Logging
SQLAlchemy event listeners automatically capture:
- CREATE: When entities are created
- UPDATE: When entities are modified (with old/new values)
- DELETE: When entities are deleted

### Graph-Like Querying
- Recursive tree traversal for lineage
- Circular reference detection
- Configurable maximum depth
- Bi-directional navigation

## Database Models

### Core Tables

1. **traceability_links** - Entity relationships
2. **audit_logs** - Immutable event log
3. **data_lineage** - Data transformation tracking
4. **requirement_traceability** - RTM records
5. **chain_of_custody** - Custody events
6. **entity_snapshots** - Version snapshots
7. **compliance_evidence** - Compliance records
8. **impact_analysis** - Change impact assessments

## Usage Examples

### Python Client Example

```python
import requests

API_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Get forward traceability
response = requests.get(
    f"{API_URL}/traceability/forward/document/1?max_depth=5",
    headers=headers
)
tree = response.json()
print(f"Total downstream dependencies: {tree['total_dependencies']}")

# Search audit logs
search_response = requests.post(
    f"{API_URL}/traceability/audit-logs/search",
    headers=headers,
    json={
        "entity_type": "document",
        "entity_id": 1,
        "action": "update",
        "limit": 50
    }
)
audit_records = search_response.json()

# Verify audit integrity
integrity_response = requests.get(
    f"{API_URL}/traceability/audit-logs/verify-integrity",
    headers=headers
)
integrity = integrity_response.json()
if integrity['integrity_intact']:
    print("✅ Audit chain verified")
```

### JavaScript Client Example

```javascript
const API_URL = 'http://localhost:8000/api/v1';
const headers = {
  'Authorization': 'Bearer YOUR_TOKEN',
  'Content-Type': 'application/json'
};

// Create traceability link
async function createLink() {
  const response = await fetch(`${API_URL}/traceability/links`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      source_entity_type: 'document',
      source_entity_id: 1,
      target_entity_type: 'form_record',
      target_entity_id: 10,
      link_type: 'derived_from',
      description: 'Form based on this procedure'
    })
  });
  return await response.json();
}

// Get RTM coverage
async function getRTMCoverage() {
  const response = await fetch(`${API_URL}/traceability/requirements/coverage`, {
    method: 'GET',
    headers: headers
  });
  const rtm = await response.json();
  console.log(`Coverage: ${rtm.summary.coverage_percentage}%`);
}
```

## Compliance Features

### ISO 17025 Requirements Covered
- ✅ 6.4.6: Equipment records and calibration
- ✅ 7.5: Technical records
- ✅ 8.4: Handling test items
- ✅ 8.8: Reporting results

### ISO 9001 Requirements Covered
- ✅ 7.1.5: Monitoring and measuring resources
- ✅ 7.5: Documented information
- ✅ 8.5: Production and service provision
- ✅ 10.2: Nonconformity and corrective action

### 21 CFR Part 11 (Electronic Records)
- ✅ Audit trails for all changes
- ✅ Immutable event log
- ✅ Time-stamped signatures
- ✅ Secure, tamper-proof records

## Performance Considerations

### Indexing
All foreign keys and frequently queried fields are indexed:
- `entity_type + entity_id` composite indexes
- `user_id + created_at` for user activity
- `event_sequence` for audit chain traversal

### Pagination
All search endpoints support pagination:
- `limit`: Max records to return (default: 100, max: 1000)
- `offset`: Skip records for pagination

### Caching
Consider caching:
- Forward/backward traceability trees (TTL: 5 minutes)
- RTM coverage reports (TTL: 1 hour)
- Compliance reports (TTL: 1 day)

## Security

### Access Control
- All endpoints require authentication
- Role-based access control via `get_current_user`
- Sensitive operations require elevated permissions

### Audit Context
Request context is automatically captured:
```python
from backend.services import set_audit_context

set_audit_context(
    user_id=current_user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    location="Lab 1, Building A",
    reason="Updating test results after review"
)
```

### Data Integrity
- Checksums prevent tampering
- Event chain verification detects modifications
- Write-once audit logs

## Integration Guide

### 1. Enable Audit Listeners
Already configured in `main.py` startup event.

### 2. Set Audit Context in API Endpoints
```python
from backend.services import set_audit_context, clear_audit_context

@router.post("/my-endpoint")
async def my_endpoint(request: Request, current_user: User = Depends(get_current_user)):
    set_audit_context(
        user_id=current_user.id,
        ip_address=request.client.host,
        reason="Business reason for this action"
    )

    try:
        # Your business logic here
        pass
    finally:
        clear_audit_context()
```

### 3. Create Traceability Links
```python
from backend.services import TraceabilityService

service = TraceabilityService(db)
service.create_traceability_link(
    source_entity_type=EntityTypeEnum.DOCUMENT,
    source_entity_id=parent_doc_id,
    target_entity_type=EntityTypeEnum.DOCUMENT,
    target_entity_id=child_doc_id,
    link_type="parent",
    created_by_id=current_user.id
)
```

## Troubleshooting

### Audit logs not being created
1. Check audit listeners are registered: Look for "✓ Audit event listeners registered" in startup logs
2. Verify audit context is set before operations
3. Check database table exists: `audit_logs`

### Integrity verification fails
1. Export audit logs for manual review
2. Check for direct database modifications (bypass SQLAlchemy)
3. Verify no manual tampering with audit_logs table

### Performance issues with deep trees
1. Reduce `max_depth` parameter
2. Implement caching for frequently accessed trees
3. Consider pagination for large result sets

## Future Enhancements

- [ ] Neo4j integration for advanced graph queries
- [ ] Real-time traceability notifications
- [ ] ML-based impact prediction
- [ ] Blockchain integration for ultimate immutability
- [ ] Advanced visualization (Sankey diagrams, force-directed graphs)

## Support

For issues or questions:
- GitHub Issues: [lims-qms-platform/issues](https://github.com/ganeshgowri-asa-et/lims-qms-platform/issues)
- Documentation: [docs/](../docs/)
- API Documentation: http://localhost:8000/api/docs
