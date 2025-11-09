# Session 4: Training & Competency Management

## Overview
Comprehensive Training & Competency Management System for ISO 17025/9001 compliant laboratories with automated gap analysis, certificate generation, and QSF forms.

## Features Implemented

### 1. Training Master Management
- **CRUD Operations** for training programs
- Training categories: Technical, Safety, Quality, Soft Skills, Compliance
- Training types: Internal, External, On-the-job, E-learning
- Duration and validity period tracking
- Competency levels: Basic, Intermediate, Advanced, Expert
- Applicable job roles mapping

### 2. Employee Training Matrix
- Individual training requirement tracking
- Current vs target competency levels
- Training status monitoring:
  - Required
  - In Progress
  - Completed
  - Expired
- Certificate validity tracking
- Competency score tracking

### 3. Training Attendance Management
- **Training session records** with:
  - Attendance tracking (Present/Absent/Partial)
  - Pre-test, post-test, and practical scores
  - Overall score calculation
  - Pass/Fail determination
  - Trainer details and qualifications
  - Feedback ratings and comments
- **Automatic matrix updates** when attendance is recorded
- Certificate number generation

### 4. Competency Gap Analysis
Comprehensive gap analysis with multiple dimensions:

**Gap Status Categories:**
- **Expired**: Certificates that have expired
- **Expiring Soon**: Valid for ≤30 days
- **Not Trained**: No training completed
- **Gap Exists**: Current level ≠ Target level
- **Competent**: All requirements met

**Analysis Features:**
- Department-wise gap analysis
- Individual employee development plans
- Training compliance metrics
- Days until certificate expiry tracking

**API Endpoints:**
```
GET /api/training/competency-gaps
    ?department=Testing
    &gap_status=Expired

GET /api/training/employee/{employee_id}/development-plan

GET /api/training/department/{department}/competency-overview
```

### 5. Auto-Certificate Generation
Professional training certificates with:

**Features:**
- PDF generation using ReportLab
- Elegant certificate design with borders
- Certificate numbering: `TRN-YYYYMM-EMPID-DD`
- QR code for verification
- Validity period display
- Training details:
  - Employee information
  - Training name and date
  - Duration and trainer
  - Assessment scores
  - Certificate issue and expiry dates
- Organization branding
- Authorized signatory section
- Computer-generated certificate disclaimer

**Templates:**
- Default professional template
- Landscape A4 format
- Blue color scheme (#1a5490)

**API Endpoints:**
```
POST /api/training/certificates/generate
{
    "attendance_id": 1,
    "template": "default"
}

POST /api/training/certificates/batch-generate
{
    "attendance_ids": [1, 2, 3],
    "template": "default"
}
```

### 6. QSF Forms Generation

#### QSF0203 - Training Attendance Record
**Purpose**: Official record of training attendance for each session

**Sections:**
1. Training Details
   - Training code, name, category, type
   - Date, duration, trainer, location
2. Attendance Register
   - S.No, Employee ID, Name, Department
   - Signature, Time In, Time Out
3. Approval Section
   - Prepared By, Reviewed By, Approved By
   - Signatures and dates

**API:**
```
POST /api/training/qsf/attendance-record
{
    "training_id": 1,
    "training_date": "2024-01-15",
    "attendees": [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "department": "Testing"
        }
    ]
}
```

#### QSF0205 - Training Effectiveness Evaluation
**Purpose**: Assess training effectiveness through multiple criteria

**Evaluation Criteria (1-5 scale):**
1. **Knowledge Retention**: Information retained post-training
2. **Practical Application**: Ability to apply learned skills
3. **Behavior Change**: Observable changes in work behavior
4. **Business Impact**: Measurable impact on operations
5. **Overall Effectiveness**: Composite effectiveness score

**Sections:**
- Employee and training details
- Evaluation criteria ratings
- Evaluator comments
- Follow-up actions required (Yes/No)
- Evaluator signature and date

**API:**
```
POST /api/training/qsf/effectiveness-evaluation
{
    "attendance_id": 1,
    "evaluation_data": {
        "knowledge_retention": 4,
        "practical_application": 5,
        "behavior_change": 4,
        "business_impact": 4,
        "overall_effectiveness": 4.25,
        "comments": "Excellent improvement in practical skills",
        "follow_up_required": false
    }
}
```

#### QSF0206 - Training Needs Assessment
**Purpose**: Identify and plan training requirements for departments

**Sections:**
1. Department and Assessment Details
   - Department name
   - Assessment period
   - Prepared by and date
2. Identified Training Needs Table
   - Training Topic
   - Target Group
   - Priority (High/Medium/Low)
   - Proposed Date
   - Estimated Cost
3. Approval Section
   - Department Head
   - HR Manager
   - Management Approval

**API:**
```
POST /api/training/qsf/needs-assessment
{
    "department": "Testing",
    "assessment_data": {
        "period": "Q1 2024",
        "prepared_by": "John Doe",
        "training_needs": [
            {
                "topic": "Advanced Testing Techniques",
                "target_group": "Test Engineers",
                "priority": "High",
                "proposed_date": "2024-02-15",
                "cost": "$5000"
            }
        ]
    }
}
```

## Database Schema

### training_master
```sql
- id (PK)
- training_code (UNIQUE)
- training_name
- description
- category
- type
- duration_hours
- validity_months
- trainer
- training_material_path
- prerequisites
- competency_level
- applicable_roles (ARRAY)
- status
- created_by
- created_at
- updated_at
```

### employee_training_matrix
```sql
- id (PK)
- employee_id
- employee_name
- department
- job_role
- training_id (FK)
- required
- current_level
- target_level
- last_trained_date
- certificate_valid_until
- status
- competency_score
- competency_status
- gap_analysis
- UNIQUE(employee_id, training_id)
```

### training_attendance
```sql
- id (PK)
- training_id (FK)
- training_date
- training_end_date
- location
- trainer_name
- trainer_qualification
- employee_id
- employee_name
- department
- attendance_status
- pre_test_score
- post_test_score
- practical_score
- overall_score
- pass_fail
- certificate_number
- certificate_issue_date
- certificate_valid_until
- certificate_path
- feedback_rating (1-5)
- feedback_comments
- effectiveness_score
- qsf_form
- form_path
- created_by
```

### training_effectiveness
```sql
- id (PK)
- attendance_id (FK)
- evaluation_date
- evaluator
- knowledge_retention
- practical_application
- behavior_change
- business_impact
- overall_effectiveness
- comments
- follow_up_required
- follow_up_date
```

### competency_assessment
```sql
- id (PK)
- employee_id
- employee_name
- assessment_date
- assessor
- job_role
- competencies (JSONB)
- overall_competency_level
- gaps_identified
- development_plan
- next_assessment_date
- status
```

## API Endpoints Summary

### Training Programs
- `POST /api/training/trainings` - Create training
- `GET /api/training/trainings` - List trainings
- `GET /api/training/trainings/{id}` - Get training
- `PUT /api/training/trainings/{id}` - Update training
- `DELETE /api/training/trainings/{id}` - Delete training

### Training Matrix
- `POST /api/training/matrix` - Create matrix entry
- `GET /api/training/matrix` - List matrix entries
- `PUT /api/training/matrix/{id}` - Update matrix entry

### Training Attendance
- `POST /api/training/attendance` - Record attendance
- `GET /api/training/attendance` - List attendance
- `GET /api/training/attendance/{id}` - Get attendance
- `PUT /api/training/attendance/{id}` - Update attendance

### Competency Analysis
- `GET /api/training/competency-gaps` - Gap analysis
- `GET /api/training/employee/{id}/development-plan` - Dev plan
- `GET /api/training/department/{dept}/competency-overview` - Dept overview

### Competency Assessment
- `POST /api/training/competency-assessment` - Create assessment
- `GET /api/training/competency-assessment` - List assessments

### Certificates
- `POST /api/training/certificates/generate` - Generate certificate
- `POST /api/training/certificates/batch-generate` - Batch generate

### QSF Forms
- `POST /api/training/qsf/attendance-record` - QSF0203
- `POST /api/training/qsf/effectiveness-evaluation` - QSF0205
- `POST /api/training/qsf/needs-assessment` - QSF0206

## Streamlit UI

### Dashboard Modules
1. **📊 Dashboard** - Overview with metrics and charts
2. **📚 Training Programs** - Manage training catalog
3. **👥 Training Matrix** - Employee training requirements
4. **📝 Training Attendance** - Record attendance and scores
5. **🎯 Competency Gap Analysis** - Identify and track gaps
6. **📜 Certificates** - Generate training certificates
7. **📄 QSF Forms** - Generate quality system forms

### Key Features
- Interactive filters and search
- Real-time data visualization with Plotly
- Form-based data entry
- Export capabilities
- Multi-tab interfaces for better organization

## ISO Compliance

### ISO 17025:2017 Requirements
✅ **6.2.2 Personnel Competence**
- Training records maintained
- Competency demonstrated and documented
- Training effectiveness evaluated

✅ **6.2.3 Personnel**
- Training needs identified
- Required training provided
- Effectiveness of training evaluated

✅ **6.2.6 Authorization**
- Competency-based authorization tracking
- Validity period monitoring

### ISO 9001:2015 Requirements
✅ **7.2 Competence**
- Competency requirements determined
- Training provided to achieve competency
- Effectiveness evaluated
- Documented information maintained

✅ **7.3 Awareness**
- Training awareness programs
- Effectiveness feedback

## Usage Example

### 1. Create Training Program
```python
import requests

response = requests.post("http://localhost:8000/api/training/trainings", json={
    "training_code": "TRN-001",
    "training_name": "Safety Awareness Training",
    "category": "Safety",
    "type": "Internal",
    "duration_hours": 4,
    "validity_months": 12,
    "trainer": "Safety Officer",
    "competency_level": "Basic",
    "created_by": "Admin"
})
```

### 2. Assign Training to Employee
```python
response = requests.post("http://localhost:8000/api/training/matrix", json={
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "department": "Testing",
    "job_role": "Test Engineer",
    "training_id": 1,
    "required": True,
    "target_level": "Basic"
})
```

### 3. Record Attendance
```python
response = requests.post("http://localhost:8000/api/training/attendance", json={
    "training_id": 1,
    "training_date": "2024-01-15",
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "department": "Testing",
    "attendance_status": "Present",
    "pre_test_score": 60,
    "post_test_score": 85,
    "practical_score": 90,
    "overall_score": 87.5,
    "pass_fail": "Pass",
    "trainer_name": "Safety Officer",
    "feedback_rating": 5,
    "created_by": "Admin"
})
```

### 4. Analyze Gaps
```python
response = requests.get("http://localhost:8000/api/training/competency-gaps", params={
    "department": "Testing",
    "gap_status": "Expired"
})
```

### 5. Generate Certificate
```python
response = requests.post("http://localhost:8000/api/training/certificates/generate", json={
    "attendance_id": 1,
    "template": "default"
})
```

## File Outputs

### Certificates
- Location: `uploads/certificates/`
- Naming: `CERT_TRN-YYYYMM-EMPID-DD.pdf`
- Format: PDF with QR code

### QSF Forms
- Location: `uploads/qsf_forms/`
- Naming:
  - `QSF0203_Training_Attendance_YYYYMMDD.pdf`
  - `QSF0205_Effectiveness_EMPID_YYYYMMDD.pdf`
  - `QSF0206_TNA_Department_YYYYMMDD.pdf`

## Testing

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- Test all endpoints interactively
- View request/response schemas
- Try example queries

## Next Steps

1. **Integrate with Session 3**: Link training to equipment operation authorization
2. **Add notifications**: Email alerts for certificate expiry
3. **Enhance reports**: Custom report generation
4. **Add analytics**: Training ROI, effectiveness trends
5. **Mobile app**: QR code scanning for attendance

## Support

For issues or questions, refer to:
- API Documentation: http://localhost:8000/docs
- Project Structure: PROJECT_STRUCTURE.md
- Database Schema: database/schema.sql
