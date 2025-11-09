"""
CRM and Customer Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class LeadStatusEnum(str, enum.Enum):
    """Lead status"""
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"


class OrderStatusEnum(str, enum.Enum):
    """Customer order status"""
    DRAFT = "Draft"
    CONFIRMED = "Confirmed"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class TicketStatusEnum(str, enum.Enum):
    """Support ticket status"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    WAITING_ON_CUSTOMER = "Waiting on Customer"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class TicketPriorityEnum(str, enum.Enum):
    """Support ticket priority"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Lead(BaseModel):
    """Lead model"""
    __tablename__ = 'leads'

    lead_number = Column(String(100), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(String(100), nullable=True)  # Website, Referral, Trade Show, etc.
    status = Column(Enum(LeadStatusEnum), default=LeadStatusEnum.NEW)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    estimated_value = Column(Float, nullable=True)
    expected_close_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    interactions = Column(JSON, nullable=True)  # Log of interactions
    converted_to_customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    converted_at = Column(String(255), nullable=True)


class Customer(BaseModel):
    """Customer model"""
    __tablename__ = 'customers'

    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)
    industry = Column(String(100), nullable=True)

    # Address
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    # Tax details
    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(50), nullable=True)

    # Business info
    customer_type = Column(String(100), nullable=True)  # Enterprise, SME, Individual
    account_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    credit_limit = Column(Float, nullable=True)
    payment_terms = Column(String(200), nullable=True)
    rating = Column(Float, nullable=True)  # 0-5 rating

    # Relationships
    orders = relationship('Order', back_populates='customer', foreign_keys='Order.customer_id')
    support_tickets = relationship('SupportTicket', back_populates='customer')


class Order(BaseModel):
    """Customer order model"""
    __tablename__ = 'customer_orders'

    order_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.DRAFT)

    # Order details
    items = Column(JSON, nullable=False)  # List of products/services
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')

    # Customer requirements
    requirements = Column(Text, nullable=True)
    specifications = Column(JSON, nullable=True)
    test_standards = Column(JSON, nullable=True)  # IEC standards required

    # Assignment
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Documents
    po_file_path = Column(String(500), nullable=True)  # Customer PO
    contract_file_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship('Customer', back_populates='orders', foreign_keys=[customer_id])


class SupportTicket(BaseModel):
    """Customer support ticket"""
    __tablename__ = 'support_tickets'

    ticket_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('customer_orders.id'), nullable=True)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # Technical, Billing, General
    priority = Column(Enum(TicketPriorityEnum), default=TicketPriorityEnum.MEDIUM)
    status = Column(Enum(TicketStatusEnum), default=TicketStatusEnum.OPEN)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reported_by_email = Column(String(255), nullable=True)
    reported_by_phone = Column(String(20), nullable=True)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(String(255), nullable=True)
    closed_at = Column(String(255), nullable=True)
    attachments = Column(JSON, nullable=True)
    communication_log = Column(JSON, nullable=True)  # Log of all communications

    # Relationships
    customer = relationship('Customer', back_populates='support_tickets')
