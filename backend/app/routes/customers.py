"""
API routes for Customer management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.numbering import NumberingService

router = APIRouter()


@router.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""

    # Generate customer code (CUST-YYYY-XXXXX)
    # Use the numbering service pattern
    customer_code = f"CUST-{NumberingService._get_next_sequence(db, 'CUST')}"

    db_customer = Customer(
        customer_code=customer_code,
        **customer.model_dump()
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all customers with optional filters"""

    query = db.query(Customer)

    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)

    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a customer by ID"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.get("/customers/code/{customer_code}", response_model=CustomerResponse)
def get_customer_by_code(customer_code: str, db: Session = Depends(get_db)):
    """Get a customer by customer code"""

    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Update a customer"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Update fields
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return None
