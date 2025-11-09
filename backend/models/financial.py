"""
Financial and Accounting models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class ExpenseStatusEnum(str, enum.Enum):
    """Expense status"""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"


class InvoiceTypeEnum(str, enum.Enum):
    """Invoice type"""
    PROFORMA = "Proforma"
    TAX_INVOICE = "Tax Invoice"
    CREDIT_NOTE = "Credit Note"
    DEBIT_NOTE = "Debit Note"


class PaymentStatusEnum(str, enum.Enum):
    """Payment status"""
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class Expense(BaseModel):
    """Expense model"""
    __tablename__ = 'expenses'

    expense_number = Column(String(100), unique=True, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    expense_date = Column(Date, nullable=False)
    category = Column(String(100), nullable=False)  # Travel, Food, Supplies, etc.
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    receipt_path = Column(String(500), nullable=True)
    status = Column(Enum(ExpenseStatusEnum), default=ExpenseStatusEnum.DRAFT)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(String(255), nullable=True)
    approver_comments = Column(Text, nullable=True)
    reimbursement_date = Column(Date, nullable=True)
    payment_reference = Column(String(200), nullable=True)


class Invoice(BaseModel):
    """Invoice model"""
    __tablename__ = 'invoices'

    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_type = Column(Enum(InvoiceTypeEnum), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('customer_orders.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # Billing details
    bill_to_name = Column(String(255), nullable=False)
    bill_to_address = Column(Text, nullable=True)
    bill_to_gst = Column(String(50), nullable=True)

    # Items and amounts
    items = Column(JSON, nullable=False)  # List of line items
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')

    # Payment
    payment_terms = Column(String(200), nullable=True)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)

    # Other
    notes = Column(Text, nullable=True)
    generated_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    file_path = Column(String(500), nullable=True)

    # Relationships
    payments = relationship('Payment', back_populates='invoice')


class Payment(BaseModel):
    """Payment model"""
    __tablename__ = 'payments'

    payment_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')
    payment_method = Column(String(100), nullable=True)  # Bank Transfer, Cash, Cheque, UPI
    reference_number = Column(String(200), nullable=True)
    bank_name = Column(String(200), nullable=True)
    transaction_id = Column(String(200), nullable=True)
    received_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    invoice = relationship('Invoice', back_populates='payments')


class Revenue(BaseModel):
    """Revenue tracking"""
    __tablename__ = 'revenues'

    revenue_date = Column(Date, nullable=False)
    source = Column(String(200), nullable=False)  # Product Sales, Services, Consulting
    category = Column(String(100), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('customer_orders.id'), nullable=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')
    cost = Column(Float, nullable=True)  # Cost of goods/services
    profit = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
