# Traceability API - Quick Start Examples

## cURL Examples

### 1. Create Traceability Link
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/links" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_type": "document",
    "source_entity_id": 1,
    "target_entity_type": "form_record",
    "target_entity_id": 10,
    "link_type": "parent",
    "description": "Form derived from this procedure"
  }'
```

### 2. Get Forward Traceability
```bash
curl -X GET "http://localhost:8000/api/v1/traceability/forward/document/1?max_depth=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Search Audit Logs
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/audit-logs/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "document",
    "entity_id": 1,
    "action": "update",
    "limit": 50
  }'
```

### 4. Verify Audit Chain Integrity
```bash
curl -X GET "http://localhost:8000/api/v1/traceability/audit-logs/verify-integrity" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Track Data Lineage
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/data-lineage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_type": "test_result",
    "source_entity_id": 100,
    "source_stage": "bronze",
    "target_entity_type": "test_result",
    "target_entity_id": 101,
    "target_stage": "silver",
    "transformation_type": "cleaning",
    "transformation_logic": "Remove outliers using 3-sigma rule",
    "data_quality_score": 95.5
  }'
```

### 6. Create Requirement
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/requirements" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_number": "REQ-ISO17025-001",
    "requirement_title": "Equipment Calibration",
    "requirement_source": "ISO 17025:2017 6.4.6",
    "requirement_category": "Equipment",
    "requirement_priority": "critical",
    "compliance_standards": ["ISO 17025", "ISO 9001"]
  }'
```

### 7. Get RTM Coverage Report
```bash
curl -X GET "http://localhost:8000/api/v1/traceability/requirements/coverage" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Record Chain of Custody Event
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/chain-of-custody" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "sample",
    "entity_id": 100,
    "entity_identifier": "SAMPLE-2025-001",
    "event_type": "transferred",
    "from_user_id": 10,
    "to_user_id": 15,
    "from_location": "Lab 1",
    "to_location": "Lab 2",
    "condition_before": "sealed, 4°C",
    "condition_after": "sealed, 4°C"
  }'
```

### 9. Create Entity Snapshot
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/snapshots" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "document",
    "entity_id": 1,
    "snapshot_data": {
      "title": "Quality Manual",
      "version": "2.0",
      "content": "Updated quality procedures..."
    },
    "snapshot_trigger": "approval"
  }'
```

### 10. Generate Compliance Report
```bash
curl -X POST "http://localhost:8000/api/v1/traceability/compliance-reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "standards": ["ISO 17025", "ISO 9001"],
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z"
  }'
```

## Complete Workflow Example

### Scenario: Document Approval with Full Traceability

```bash
# 1. Create document (automatic audit log via event listener)
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Procedure TP-001",
    "document_type": "procedure",
    "level": 3,
    "content": "Detailed test procedure..."
  }'
# Response: {"id": 100, ...}

# 2. Create snapshot before approval
curl -X POST "http://localhost:8000/api/v1/traceability/snapshots" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "document",
    "entity_id": 100,
    "snapshot_data": {"title": "Test Procedure TP-001", "status": "draft"},
    "snapshot_trigger": "pre_approval"
  }'

# 3. Approve document (automatic audit log)
curl -X PUT "http://localhost:8000/api/v1/documents/100/approve" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Link to parent policy document
curl -X POST "http://localhost:8000/api/v1/traceability/links" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_type": "document",
    "source_entity_id": 1,
    "target_entity_type": "document",
    "target_entity_id": 100,
    "link_type": "child"
  }'

# 5. Create requirement link
curl -X POST "http://localhost:8000/api/v1/traceability/requirements/link" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_id": 5,
    "entity_type": "document",
    "entity_id": 100,
    "verification_method": "inspection"
  }'

# 6. Get complete audit history
curl -X GET "http://localhost:8000/api/v1/traceability/audit-logs/document/100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 7. Check impact if we modify this document
curl -X POST "http://localhost:8000/api/v1/traceability/impact-analysis" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "document",
    "entity_id": 100,
    "change_description": "Updating test method"
  }'
```

## Python SDK Examples

```python
import requests
from datetime import datetime

class TraceabilityClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def create_link(self, source_type, source_id, target_type, target_id, link_type):
        """Create traceability link"""
        response = requests.post(
            f"{self.base_url}/traceability/links",
            headers=self.headers,
            json={
                "source_entity_type": source_type,
                "source_entity_id": source_id,
                "target_entity_type": target_type,
                "target_entity_id": target_id,
                "link_type": link_type
            }
        )
        return response.json()

    def get_forward_trace(self, entity_type, entity_id, max_depth=5):
        """Get forward traceability"""
        response = requests.get(
            f"{self.base_url}/traceability/forward/{entity_type}/{entity_id}",
            headers=self.headers,
            params={"max_depth": max_depth}
        )
        return response.json()

    def search_audit_logs(self, entity_type=None, entity_id=None, action=None, limit=100):
        """Search audit logs"""
        response = requests.post(
            f"{self.base_url}/traceability/audit-logs/search",
            headers=self.headers,
            json={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": action,
                "limit": limit
            }
        )
        return response.json()

    def verify_integrity(self):
        """Verify audit chain integrity"""
        response = requests.get(
            f"{self.base_url}/traceability/audit-logs/verify-integrity",
            headers=self.headers
        )
        return response.json()

    def get_rtm_coverage(self):
        """Get RTM coverage report"""
        response = requests.get(
            f"{self.base_url}/traceability/requirements/coverage",
            headers=self.headers
        )
        return response.json()

# Usage
client = TraceabilityClient("http://localhost:8000/api/v1", "YOUR_TOKEN")

# Create link
link = client.create_link("document", 1, "form_record", 10, "parent")
print(f"Link created: {link['id']}")

# Get forward trace
tree = client.get_forward_trace("document", 1, max_depth=5)
print(f"Downstream dependencies: {tree['total_dependencies']}")

# Search audit logs
logs = client.search_audit_logs(entity_type="document", entity_id=1)
print(f"Found {logs['total']} audit records")

# Verify integrity
integrity = client.verify_integrity()
if integrity['integrity_intact']:
    print("✅ Audit chain verified")
else:
    print(f"❌ Integrity issues: {integrity['issues_found']}")

# Get RTM coverage
rtm = client.get_rtm_coverage()
print(f"Requirements coverage: {rtm['summary']['coverage_percentage']}%")
```

## TypeScript/JavaScript Examples

```typescript
interface TraceabilityClient {
  baseUrl: string;
  token: string;
}

class TraceabilityAPI implements TraceabilityClient {
  constructor(public baseUrl: string, public token: string) {}

  private get headers() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async createLink(
    sourceType: string,
    sourceId: number,
    targetType: string,
    targetId: number,
    linkType: string
  ) {
    const response = await fetch(`${this.baseUrl}/traceability/links`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        source_entity_type: sourceType,
        source_entity_id: sourceId,
        target_entity_type: targetType,
        target_entity_id: targetId,
        link_type: linkType
      })
    });
    return await response.json();
  }

  async getForwardTrace(entityType: string, entityId: number, maxDepth: number = 5) {
    const response = await fetch(
      `${this.baseUrl}/traceability/forward/${entityType}/${entityId}?max_depth=${maxDepth}`,
      { headers: this.headers }
    );
    return await response.json();
  }

  async searchAuditLogs(filters: {
    entityType?: string;
    entityId?: number;
    action?: string;
    limit?: number;
  }) {
    const response = await fetch(`${this.baseUrl}/traceability/audit-logs/search`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(filters)
    });
    return await response.json();
  }

  async verifyIntegrity() {
    const response = await fetch(
      `${this.baseUrl}/traceability/audit-logs/verify-integrity`,
      { headers: this.headers }
    );
    return await response.json();
  }

  async getRTMCoverage() {
    const response = await fetch(
      `${this.baseUrl}/traceability/requirements/coverage`,
      { headers: this.headers }
    );
    return await response.json();
  }
}

// Usage
const api = new TraceabilityAPI('http://localhost:8000/api/v1', 'YOUR_TOKEN');

// Create link
const link = await api.createLink('document', 1, 'form_record', 10, 'parent');
console.log(`Link created: ${link.id}`);

// Get forward trace
const tree = await api.getForwardTrace('document', 1, 5);
console.log(`Downstream dependencies: ${tree.total_dependencies}`);

// Search audit logs
const logs = await api.searchAuditLogs({
  entityType: 'document',
  entityId: 1,
  limit: 100
});
console.log(`Found ${logs.total} audit records`);

// Verify integrity
const integrity = await api.verifyIntegrity();
if (integrity.integrity_intact) {
  console.log('✅ Audit chain verified');
} else {
  console.log(`❌ Integrity issues: ${integrity.issues_found}`);
}

// Get RTM coverage
const rtm = await api.getRTMCoverage();
console.log(`Requirements coverage: ${rtm.summary.coverage_percentage}%`);
```

## Testing with Postman

1. Import the OpenAPI schema from: `http://localhost:8000/api/openapi.json`
2. Create environment variable: `token` with your JWT token
3. Use `{{token}}` in Authorization header
4. All endpoints are documented with examples

## Common Patterns

### Pattern 1: Complete Audit Trail
```bash
# Get entity history
GET /api/v1/traceability/audit-logs/document/100

# Export for compliance
POST /api/v1/traceability/audit-logs/export?entity_type=document&entity_id=100

# Verify integrity
GET /api/v1/traceability/audit-logs/verify-integrity
```

### Pattern 2: Document Lineage
```bash
# Get downstream (what depends on this?)
GET /api/v1/traceability/forward/document/100

# Get upstream (what does this depend on?)
GET /api/v1/traceability/backward/document/100

# Check impact of changes
POST /api/v1/traceability/impact-analysis
```

### Pattern 3: Data Quality Pipeline
```bash
# Track Bronze → Silver
POST /api/v1/traceability/data-lineage
{"source_stage": "bronze", "target_stage": "silver", ...}

# Track Silver → Gold
POST /api/v1/traceability/data-lineage
{"source_stage": "silver", "target_stage": "gold", ...}

# Get complete pipeline
GET /api/v1/traceability/data-lineage/test_result/100
```

### Pattern 4: Compliance Audit
```bash
# Get RTM coverage
GET /api/v1/traceability/requirements/coverage

# Generate compliance report
POST /api/v1/traceability/compliance-reports
{"standards": ["ISO 17025"], "start_date": "2025-01-01", ...}

# Export audit logs
POST /api/v1/traceability/audit-logs/export?format=json
```
