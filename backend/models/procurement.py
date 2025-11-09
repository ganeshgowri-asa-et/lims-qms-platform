"""
Procurement and Equipment Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class RFQStatusEnum(str, enum.Enum):
    """RFQ status"""
    DRAFT = "Draft"
    SENT = "Sent"
    RECEIVED = "Received"
    AWARDED = "Awarded"
    CANCELLED = "Cancelled"


class POStatusEnum(str, enum.Enum):
    """Purchase Order status"""
    DRAFT = "Draft"
    APPROVED = "Approved"
    SENT = "Sent"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class EquipmentStatusEnum(str, enum.Enum):
    """Equipment status"""
    ACTIVE = "Active"
    UNDER_CALIBRATION = "Under Calibration"
    UNDER_MAINTENANCE = "Under Maintenance"
    INACTIVE = "Inactive"
    RETIRED = "Retired"


class Vendor(BaseModel):
    """Vendor model"""
    __tablename__ = 'vendors'

    vendor_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)
    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(50), nullable=True)
    bank_details = Column(JSON, nullable=True)
    rating = Column(Float, nullable=True)  # 0-5 rating
    is_approved = Column(Boolean, default=False)
    approved_categories = Column(JSON, nullable=True)  # List of product/service categories

    # Relationships
    rfqs = relationship('RFQ', back_populates='vendor')
    purchase_orders = relationship('PurchaseOrder', back_populates='vendor')


class RFQ(BaseModel):
    """Request for Quotation"""
    __tablename__ = 'rfqs'

    rfq_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=True)
    requested_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(RFQStatusEnum), default=RFQStatusEnum.DRAFT)
    items = Column(JSON, nullable=False)  # List of items with specs
    quotation_received = Column(JSON, nullable=True)
    quotation_file = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    vendor = relationship('Vendor', back_populates='rfqs')


class PurchaseOrder(BaseModel):
    """Purchase Order"""
    __tablename__ = 'purchase_orders'

    po_number = Column(String(100), unique=True, nullable=False, index=True)
    rfq_id = Column(Integer, ForeignKey('rfqs.id'), nullable=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    po_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    status = Column(Enum(POStatusEnum), default=POStatusEnum.DRAFT)
    items = Column(JSON, nullable=False)  # List of items with quantity and price
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    payment_terms = Column(String(200), nullable=True)
    delivery_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    approved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(String(255), nullable=True)

    # Relationships
    vendor = relationship('Vendor', back_populates='purchase_orders')


class Equipment(BaseModel):
    """Equipment/Instrument model"""
    __tablename__ = 'equipment'

    equipment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True)  # Test equipment, Calibration, IT, etc.
    manufacturer = Column(String(255), nullable=True)
    model = Column(String(200), nullable=True)
    serial_number = Column(String(200), nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    location = Column(String(200), nullable=True)
    custodian_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(Enum(EquipmentStatusEnum), default=EquipmentStatusEnum.ACTIVE)
    specifications = Column(JSON, nullable=True)
    calibration_required = Column(Boolean, default=False)
    calibration_frequency_days = Column(Integer, nullable=True)  # Days between calibrations
    last_calibration_date = Column(Date, nullable=True)
    next_calibration_date = Column(Date, nullable=True)
    documents = Column(JSON, nullable=True)  # Manuals, certificates, etc.

    # Relationships
    calibrations = relationship('Calibration', back_populates='equipment')
    maintenance_records = relationship('Maintenance', back_populates='equipment')


class Calibration(BaseModel):
    """Calibration record"""
    __tablename__ = 'calibrations'

    calibration_number = Column(String(100), unique=True, nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    calibration_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    calibrated_by = Column(String(255), nullable=True)  # External agency or internal
    certificate_number = Column(String(100), nullable=True)
    certificate_path = Column(String(500), nullable=True)
    result = Column(String(50), nullable=True)  # Pass, Fail, Conditional
    calibration_data = Column(JSON, nullable=True)
    remarks = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    next_due_date = Column(Date, nullable=True)

    # Relationships
    equipment = relationship('Equipment', back_populates='calibrations')


class Maintenance(BaseModel):
    """Equipment maintenance record"""
    __tablename__ = 'maintenance_records'

    maintenance_number = Column(String(100), unique=True, nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    maintenance_type = Column(String(100), nullable=True)  # Preventive, Corrective, Breakdown
    scheduled_date = Column(Date, nullable=True)
    actual_date = Column(Date, nullable=False)
    performed_by = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    actions_taken = Column(Text, nullable=True)
    parts_replaced = Column(JSON, nullable=True)
    cost = Column(Float, nullable=True)
    downtime_hours = Column(Float, nullable=True)
    status = Column(String(50), nullable=True)  # Scheduled, Completed, Pending
    next_maintenance_date = Column(Date, nullable=True)

    # Relationships
    equipment = relationship('Equipment', back_populates='maintenance_records')
