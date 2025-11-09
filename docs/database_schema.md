# Database Schema Documentation

## Entity Relationship Diagram

```
┌─────────────────────┐
│     customers       │
│─────────────────────│
│ id (PK)             │
│ customer_code       │◄─────┐
│ customer_name       │      │
│ customer_type       │      │
│ contact_person      │      │
│ email               │      │
│ phone               │      │
│ address_line1       │      │
│ city, state         │      │
│ gst_number          │      │
│ is_active           │      │
│ created_at          │      │
└─────────────────────┘      │
                             │
                             │ 1:N
┌─────────────────────────┐  │
│   test_requests         │  │
│─────────────────────────│  │
│ id (PK)                 │  │
│ trq_number (UNIQUE)     │  │
│ customer_id (FK)        │──┘
│ project_name            │
│ test_type               │
│ priority                │
│ status                  │
│ request_date            │
│ due_date                │
│ description             │
│ quote_required          │
│ quote_number            │
│ quote_amount            │
│ quote_approved          │
│ requested_by            │
│ barcode_data            │
│ created_at              │
└─────────────────────────┘
          │
          │ 1:N
          ├─────────────────────────────┐
          │                             │
          ▼                             ▼
┌─────────────────────┐    ┌──────────────────────┐
│      samples        │    │  test_parameters     │
│─────────────────────│    │──────────────────────│
│ id (PK)             │    │ id (PK)              │
│ sample_number       │    │ test_request_id (FK) │
│ test_request_id (FK)│    │ parameter_name       │
│ sample_name         │    │ parameter_code       │
│ sample_type         │    │ test_method          │
│ quantity            │    │ specification        │
│ unit                │    │ unit_of_measurement  │
│ batch_number        │    │ unit_price           │
│ lot_number          │    │ quantity             │
│ status              │    │ total_price          │
│ received_date       │    │ result               │
│ testing_start_date  │    │ pass_fail            │
│ testing_end_date    │    │ is_completed         │
│ storage_location    │    │ created_at           │
│ barcode_data        │    └──────────────────────┘
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│  number_sequences   │
│─────────────────────│
│ id (PK)             │
│ prefix              │
│ year                │
│ current_sequence    │
│ created_at          │
└─────────────────────┘
UNIQUE(prefix, year)
```

## Table Definitions

### customers

Customer master table storing all customer information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| customer_code | VARCHAR(50) | UNIQUE, NOT NULL | Auto-generated (CUST-YYYY-XXXXX) |
| customer_name | VARCHAR(255) | NOT NULL | Customer name |
| customer_type | VARCHAR(50) | NOT NULL | internal/external/government/academic |
| contact_person | VARCHAR(255) | | Contact person name |
| email | VARCHAR(255) | | Email address |
| phone | VARCHAR(50) | | Phone number |
| mobile | VARCHAR(50) | | Mobile number |
| address_line1 | VARCHAR(255) | | Address line 1 |
| address_line2 | VARCHAR(255) | | Address line 2 |
| city | VARCHAR(100) | | City |
| state | VARCHAR(100) | | State |
| postal_code | VARCHAR(20) | | Postal code |
| country | VARCHAR(100) | DEFAULT 'India' | Country |
| gst_number | VARCHAR(50) | | GST number |
| pan_number | VARCHAR(20) | | PAN number |
| remarks | TEXT | | Additional remarks |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |
| created_by | VARCHAR(255) | NOT NULL | Created by user |

### test_requests

Test request records with auto-generated TRQ numbers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| trq_number | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated (TRQ-YYYY-XXXXX) |
| customer_id | INTEGER | FK(customers.id) | Customer reference |
| project_name | VARCHAR(255) | NOT NULL | Project name |
| test_type | VARCHAR(100) | NOT NULL | Type of test |
| priority | VARCHAR(20) | DEFAULT 'medium' | low/medium/high/urgent |
| status | VARCHAR(50) | DEFAULT 'draft' | Current status |
| request_date | DATE | NOT NULL | Request date |
| due_date | DATE | | Due date |
| completion_date | DATE | | Completion date |
| description | TEXT | | Description |
| special_instructions | TEXT | | Special instructions |
| quote_required | BOOLEAN | DEFAULT FALSE | Quote required flag |
| quote_number | VARCHAR(20) | | Auto-generated quote number |
| quote_amount | NUMERIC(10,2) | | Quote amount |
| quote_approved | BOOLEAN | DEFAULT FALSE | Quote approved flag |
| quote_approved_by | VARCHAR(255) | | Quote approver |
| quote_approved_date | DATE | | Quote approval date |
| requested_by | VARCHAR(255) | NOT NULL | Requester name |
| department | VARCHAR(100) | | Department |
| contact_number | VARCHAR(50) | | Contact number |
| submitted_by | VARCHAR(255) | | Submitter name |
| submitted_date | DATE | | Submission date |
| approved_by | VARCHAR(255) | | Approver name |
| approved_date | DATE | | Approval date |
| barcode_data | TEXT | | Base64 barcode image |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |
| created_by | VARCHAR(255) | NOT NULL | Created by user |

### samples

Sample tracking with auto-generated sample numbers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| sample_number | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated (SMP-YYYY-XXXXX) |
| test_request_id | INTEGER | FK(test_requests.id) | Test request reference |
| sample_name | VARCHAR(255) | NOT NULL | Sample name |
| sample_type | VARCHAR(100) | NOT NULL | Type of sample |
| sample_description | TEXT | | Sample description |
| quantity | NUMERIC(10,2) | NOT NULL | Quantity |
| unit | VARCHAR(50) | NOT NULL | Unit of measurement |
| condition_on_receipt | VARCHAR(255) | | Condition on receipt |
| storage_condition | VARCHAR(255) | | Storage condition |
| expiry_date | DATE | | Expiry date |
| batch_number | VARCHAR(100) | | Batch number |
| lot_number | VARCHAR(100) | | Lot number |
| manufacturing_date | DATE | | Manufacturing date |
| status | VARCHAR(50) | DEFAULT 'pending' | Current status |
| received_date | DATE | | Received date |
| received_by | VARCHAR(255) | | Received by user |
| testing_start_date | DATE | | Testing start date |
| testing_end_date | DATE | | Testing end date |
| barcode_data | TEXT | | Base64 barcode image |
| storage_location | VARCHAR(255) | | Storage location |
| remarks | TEXT | | Remarks |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |
| created_by | VARCHAR(255) | NOT NULL | Created by user |

### test_parameters

Test parameters for each test request.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| test_request_id | INTEGER | FK(test_requests.id) | Test request reference |
| parameter_name | VARCHAR(255) | NOT NULL | Parameter name |
| parameter_code | VARCHAR(50) | | Parameter code |
| test_method | VARCHAR(255) | | Test method |
| specification | VARCHAR(255) | | Specification |
| unit_of_measurement | VARCHAR(50) | | Unit |
| acceptance_criteria | TEXT | | Acceptance criteria |
| result | VARCHAR(255) | | Test result |
| numeric_result | NUMERIC(10,4) | | Numeric result |
| pass_fail | VARCHAR(20) | | Pass/Fail/NA |
| analyzed_by | VARCHAR(255) | | Analyst name |
| analyzed_date | VARCHAR(50) | | Analysis date |
| verified_by | VARCHAR(255) | | Verifier name |
| verified_date | VARCHAR(50) | | Verification date |
| unit_price | NUMERIC(10,2) | | Unit price |
| quantity | INTEGER | DEFAULT 1 | Quantity |
| total_price | NUMERIC(10,2) | | Total price |
| is_completed | BOOLEAN | DEFAULT FALSE | Completed flag |
| remarks | TEXT | | Remarks |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

### number_sequences

Auto-numbering sequence management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| prefix | VARCHAR(10) | NOT NULL | Document prefix (TRQ, SMP, etc.) |
| year | INTEGER | NOT NULL | Year |
| current_sequence | INTEGER | DEFAULT 0 | Current sequence number |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

**Unique Constraint**: (prefix, year)

## Indexes

- customers.customer_code (UNIQUE)
- test_requests.trq_number (UNIQUE)
- test_requests.customer_id (FK)
- samples.sample_number (UNIQUE)
- samples.test_request_id (FK)
- test_parameters.test_request_id (FK)
- number_sequences.(prefix, year) (UNIQUE)

## Cascading Rules

- test_requests → samples: CASCADE DELETE
- test_requests → test_parameters: CASCADE DELETE
