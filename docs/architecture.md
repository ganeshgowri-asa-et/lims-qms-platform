# LIMS/QMS Platform Architecture

## System Overview

The LIMS/QMS Platform is a three-tier application designed for laboratory test request and sample management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│              (Streamlit - Port 8501)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Dashboard │  │Test Req  │  │ Samples  │              │
│  │  Page    │  │  Page    │  │   Page   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                        │
                   HTTP/REST
                        │
┌─────────────────────────────────────────────────────────┐
│                   Backend Layer                          │
│               (FastAPI - Port 8000)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │              API Routes                           │   │
│  │  /test-requests  /samples  /customers            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Business Logic                         │   │
│  │  NumberingService  BarcodeService  QuoteService  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Data Models (SQLAlchemy)               │   │
│  │  Customer  TestRequest  Sample  TestParameter    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        │
                   SQL/ORM
                        │
┌─────────────────────────────────────────────────────────┐
│                   Database Layer                         │
│              (PostgreSQL - Port 5432)                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Tables: customers, test_requests, samples,      │   │
│  │          test_parameters, number_sequences       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Streamlit)
- **Technology**: Python Streamlit framework
- **Port**: 8501
- **Responsibilities**:
  - User interface rendering
  - Form handling
  - API client interactions
  - Barcode display

### Backend (FastAPI)
- **Technology**: FastAPI web framework
- **Port**: 8000
- **Responsibilities**:
  - RESTful API endpoints
  - Business logic execution
  - Data validation
  - Auto-numbering
  - Barcode generation
  - Quote automation

### Database (PostgreSQL)
- **Technology**: PostgreSQL 15
- **Port**: 5432
- **Responsibilities**:
  - Data persistence
  - Transaction management
  - Referential integrity
  - Sequence management

## Data Flow

### Test Request Creation Flow

```
1. User fills form in Streamlit UI
2. Frontend validates inputs
3. Frontend calls POST /api/v1/test-requests
4. Backend validates with Pydantic schemas
5. NumberingService generates TRQ number
6. BarcodeService generates barcode
7. Database creates test_requests record
8. Database creates test_parameters records
9. Backend returns created object
10. Frontend displays TRQ number and barcode
```

### Quote Generation Flow

```
1. User clicks "Generate Quote"
2. Frontend calls POST /api/v1/test-requests/{trq}/generate-quote
3. Backend retrieves test parameters
4. QuoteService calculates prices
5. NumberingService generates quote number
6. Database updates test_request with quote info
7. Backend returns quote details
8. Frontend displays quote
```

## Security Layers

1. **Input Validation**: Pydantic schemas
2. **SQL Injection Protection**: SQLAlchemy ORM
3. **CORS**: Configured middleware
4. **Environment Variables**: Sensitive data isolation

## Scalability Considerations

- **Horizontal Scaling**: Stateless API design
- **Database Connection Pooling**: SQLAlchemy pool
- **Caching**: Can add Redis layer
- **Load Balancing**: Docker Compose ready

## Deployment Architecture

```
Docker Network: lims_network
├── lims_qms_db (PostgreSQL container)
├── lims_qms_backend (FastAPI container)
└── lims_qms_frontend (Streamlit container)
```

## Key Design Patterns

1. **Repository Pattern**: Database access through ORM
2. **Service Layer**: Business logic separation
3. **DTO Pattern**: Pydantic schemas for data transfer
4. **Factory Pattern**: Auto-numbering service
5. **Dependency Injection**: FastAPI dependencies
