# Quick Start Guide - Data Capture Engine

## 🚀 Getting Started

### 1. Start the Application

```bash
cd /home/user/lims-qms-platform

# Start backend
cd backend
uvicorn main:app --reload

# In another terminal, start frontend (optional)
cd frontend
streamlit run app.py
```

### 2. Access API Documentation

Open your browser: **http://localhost:8000/api/docs**

### 3. Quick API Test

```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login",
    data={"username": "admin", "password": "admin123"})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create a form record
record = requests.post("http://localhost:8000/api/v1/data-capture/records",
    headers=headers,
    json={
        "template_id": 1,
        "title": "My First Record",
        "values": {
            "field1": "value1",
            "field2": "value2"
        }
    }).json()

print(f"Created record: {record['record_number']}")
```

## 📖 Key Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Create record | POST | `/api/v1/data-capture/records` |
| Get record | GET | `/api/v1/data-capture/records/{id}` |
| Submit for review | POST | `/api/v1/data-capture/records/{id}/submit` |
| Review record | POST | `/api/v1/data-capture/records/{id}/review` |
| Approve record | POST | `/api/v1/data-capture/records/{id}/approve` |
| Validate data | POST | `/api/v1/data-capture/validate` |
| Save draft | POST | `/api/v1/data-capture/drafts` |
| Bulk upload | POST | `/api/v1/data-capture/bulk-upload/{template_id}` |

## 🔄 Workflow Example

```python
# 1. Create → 2. Submit → 3. Review → 4. Approve

import httpx

BASE = "http://localhost:8000/api/v1/data-capture"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 1. Create
record = httpx.post(f"{BASE}/records", json={
    "template_id": 1,
    "values": {"temp": 23.5}
}, headers=headers).json()

record_id = record["id"]

# 2. Submit
httpx.post(f"{BASE}/records/{record_id}/submit", headers=headers)

# 3. Review (as checker)
httpx.post(f"{BASE}/records/{record_id}/review",
    json={"action": "approve"}, headers=headers)

# 4. Approve (as approver)
httpx.post(f"{BASE}/records/{record_id}/approve",
    json={"action": "approve"}, headers=headers)
```

## 📚 Documentation

- **Full API Docs**: `docs/DATA_CAPTURE_ENGINE.md`
- **Examples**: `examples/data_capture_examples.py`
- **Tests**: `tests/test_data_capture.py`
- **Session Summary**: `SESSION_2_SUMMARY.md`

## ✅ Features

✅ Dynamic form generation
✅ Doer-Checker-Approver workflow
✅ Real-time validation
✅ Digital signatures
✅ Email & in-app notifications
✅ Bulk upload (CSV/Excel)
✅ Auto-save drafts
✅ Complete audit trail
✅ Duplicate detection
✅ Traceability links

## 🧪 Run Tests

```bash
cd /home/user/lims-qms-platform
pytest tests/test_data_capture.py -v
```

## 📖 Run Examples

```bash
python examples/data_capture_examples.py
```

## 🆘 Troubleshooting

**Issue**: Import errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: Database errors
```bash
# Solution: Initialize database
python backend/core/database.py
```

**Issue**: Authentication errors
```bash
# Solution: Create admin user or use existing credentials
# Default: username=admin, password=admin123
```

## 🎯 Next Steps

1. ✅ **Session 2 Complete**: Data capture engine ✓
2. 📝 **Session 3**: Frontend UI with Streamlit
3. 📊 **Session 4**: Analytics & reporting
4. 🔗 **Session 5**: External system integration

---

**Happy Coding!** 🚀

For detailed documentation, see: `docs/DATA_CAPTURE_ENGINE.md`
