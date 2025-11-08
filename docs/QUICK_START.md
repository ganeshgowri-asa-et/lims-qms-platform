# Quick Start Guide - LIMS-QMS Equipment Calibration Management

## 5-Minute Quick Start

### 1. Start the Application with Docker

```bash
# Clone and navigate to project
git clone <repository-url>
cd lims-qms-platform

# Start all services
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)
docker-compose ps
```

### 2. Create Database Tables

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

### 3. Access the API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 4. Create Your First User

**Using the API Documentation (Swagger UI):**

1. Go to http://localhost:8000/api/docs
2. Expand `POST /api/auth/register`
3. Click "Try it out"
4. Fill in the request body:

```json
{
  "username": "admin",
  "email": "admin@lims-qms.com",
  "full_name": "System Administrator",
  "password": "Admin@123",
  "role": "admin",
  "phone_number": "+1234567890",
  "department": "QA",
  "employee_id": "EMP001"
}
```

5. Click "Execute"

### 5. Login and Get Access Token

1. Expand `POST /api/auth/login`
2. Click "Try it out"
3. Fill in credentials:
   - **username**: admin
   - **password**: Admin@123
4. Click "Execute"
5. Copy the `access_token` from the response

### 6. Authorize Your Session

1. Click the "Authorize" button at the top of the Swagger UI
2. Paste your access token
3. Click "Authorize" and then "Close"

Now you're authenticated and can use all API endpoints!

## Common Workflows

### Workflow 1: Register Equipment

```json
POST /api/equipment/

{
  "equipment_name": "Digital Multimeter - Fluke 87V",
  "category": "measuring_instrument",
  "manufacturer": "Fluke",
  "model_number": "87V",
  "serial_number": "FL87V-12345",
  "department": "QA",
  "location": "Testing Lab - Room 101",
  "requires_calibration": true,
  "calibration_frequency": "yearly",
  "status": "operational",
  "specifications": [
    {
      "parameter_name": "DC Voltage",
      "measurement_range_min": 0,
      "measurement_range_max": 1000,
      "unit": "V",
      "accuracy": "±0.05%",
      "resolution": "0.001"
    }
  ]
}
```

**Response:**
- Equipment will be created with unique ID like `EQP-QA-2025-001`
- QR code will be auto-generated
- Equipment history entry will be created

### Workflow 2: Create Calibration Vendor

```json
POST /api/calibration/vendors

{
  "vendor_name": "NABL Calibration Services",
  "vendor_code": "NABL-001",
  "vendor_contact_person": "John Smith",
  "vendor_email": "john@nablcal.com",
  "vendor_phone": "+1234567890",
  "accreditation_body": "NABL",
  "accreditation_number": "C-12345",
  "is_approved": true
}
```

### Workflow 3: Record Calibration

```json
POST /api/calibration/records

{
  "equipment_id": 1,
  "calibration_type": "external",
  "calibration_date": "2025-11-01",
  "due_date": "2026-11-01",
  "vendor_id": 1,
  "certificate_number": "CAL-2025-001",
  "result": "pass",
  "calibration_cost": 500.00,
  "performed_by_id": 1
}
```

**The system will automatically:**
- Generate unique calibration ID
- Calculate next calibration date (1 year from calibration date)
- Update equipment's last and next calibration dates
- Create workflow record for approval
- Set up 30/15/7 day alerts

### Workflow 4: Submit Calibration for Approval

```json
POST /api/calibration/records/1/submit

{
  "comments": "Calibration completed successfully. All parameters within tolerance.",
  "signature_data": "base64-encoded-signature"
}
```

### Workflow 5: Check Calibrations Due

```bash
GET /api/calibration/due?days_ahead=30
```

**Response:**
```json
[
  {
    "equipment_id": 1,
    "equipment_name": "Digital Multimeter - Fluke 87V",
    "equipment_code": "QA-DIG-001",
    "department": "QA",
    "next_calibration_date": "2025-12-01",
    "days_until_due": 23,
    "calibration_frequency": "yearly",
    "is_overdue": false,
    "alert_level": "30_days"
  }
]
```

### Workflow 6: Get AI Failure Prediction

```bash
GET /api/analytics/equipment/1/failure-prediction
```

**Response:**
```json
{
  "equipment_id": 1,
  "failure_probability": 15.5,
  "confidence": "medium",
  "risk_level": "low",
  "recommendations": [
    "Equipment operating normally",
    "Continue regular monitoring"
  ],
  "data_points_analyzed": 120
}
```

### Workflow 7: Calculate Equipment OEE

```bash
GET /api/equipment/1/oee?start_date=2025-10-01&end_date=2025-10-31
```

**Response:**
```json
{
  "equipment_id": 1,
  "equipment_name": "Digital Multimeter - Fluke 87V",
  "period_start": "2025-10-01",
  "period_end": "2025-10-31",
  "average_availability": 95.5,
  "average_performance": 92.3,
  "average_quality": 98.7,
  "average_oee": 87.1,
  "total_downtime_hours": 12.5,
  "breakdown_by_type": {
    "calibration": 8.0,
    "maintenance": 3.5,
    "breakdown": 1.0
  }
}
```

## Testing the Complete System

### 1. Create Test Data

```bash
# Create equipment
curl -X POST "http://localhost:8000/api/equipment/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_name": "Test Equipment",
    "category": "measuring_instrument",
    "department": "QA",
    "location": "Lab 1",
    "requires_calibration": true,
    "calibration_frequency": "yearly",
    "status": "operational"
  }'
```

### 2. Upload Calibration Certificate (with OCR)

```bash
# Upload PDF certificate
curl -X POST "http://localhost:8000/api/calibration/records/1/certificate/upload?extract_data=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@certificate.pdf"
```

The OCR service will automatically extract:
- Certificate number
- Calibration date
- Due date
- Equipment serial number
- Measurement uncertainty
- Environmental conditions
- Reference standards used

### 3. View Dashboard Summary

```bash
GET /api/analytics/dashboard/summary
```

**Response:**
```json
{
  "total_equipment": 50,
  "operational_equipment": 47,
  "equipment_availability_rate": 94.0,
  "calibrations_due_30_days": 8,
  "overdue_calibrations": 2,
  "pending_maintenance": 5,
  "calibrations_last_30_days": 12,
  "alerts": {
    "critical": 2,
    "warning": 8
  }
}
```

## User Roles and Permissions

### Admin
- Full access to all features
- User management
- System configuration

### QA Manager
- Approve calibrations
- View all reports
- Manage vendors

### Calibration Engineer
- Create/update calibration records
- Upload certificates
- Submit for approval

### Checker
- Review submitted records
- Approve for final approval

### Approver
- Final approval of records
- View workflow status

### Doer
- Create and submit records
- Cannot approve own records

### Viewer
- Read-only access
- View reports and dashboards

## Troubleshooting

### Issue: Database connection error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Migration errors

```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Issue: Import errors in Python

```bash
# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Issue: OCR not working

```bash
# Verify Tesseract is installed in container
docker-compose exec backend tesseract --version

# Check Tesseract path in .env
TESSERACT_CMD=/usr/bin/tesseract
```

## Next Steps

1. **Configure Email/SMS Alerts**
   - Update `.env` with your email settings
   - Add Twilio credentials for SMS
   - Test alerts: `GET /api/analytics/calibration/alerts/check`

2. **Set Up Automated Calibration Reminders**
   - Create a cron job to run daily
   - Call `/api/analytics/calibration/alerts/check`
   - Sends emails/SMS for 30/15/7 day alerts

3. **Train AI Models**
   - Add equipment utilization data
   - Log equipment failures
   - Run failure prediction after 30+ days of data

4. **Generate Reports**
   - Equipment performance: `/api/analytics/reports/equipment-performance`
   - Calibration summary: `/api/analytics/reports/calibration-summary`
   - Export to Excel/PDF (future feature)

5. **Integrate with Existing Systems**
   - Use API endpoints to integrate with ERP
   - Connect to CMMS for maintenance
   - Link to document management system

## Support

Need help? Check:
- Full documentation in `/docs`
- API documentation at http://localhost:8000/api/docs
- GitHub Issues
- Email: support@lims-qms.com

---

Happy calibrating! 🔧📊
