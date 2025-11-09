"""
Form Engine API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.form import FormTemplate, FormField, FormRecord, FormValue, FieldTypeEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

router = APIRouter()


class FormFieldCreate(BaseModel):
    field_name: str
    field_label: str
    field_type: FieldTypeEnum
    is_required: bool = False
    options: Optional[List[str]] = None


class FormTemplateCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    fields: List[FormFieldCreate]


class FormRecordSubmit(BaseModel):
    template_id: int
    values: dict


@router.post("/templates", response_model=dict)
async def create_form_template(
    template: FormTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new form template"""
    # Check if code already exists
    if db.query(FormTemplate).filter(FormTemplate.code == template.code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form template with this code already exists"
        )

    new_template = FormTemplate(
        name=template.name,
        code=template.code,
        description=template.description,
        category=template.category,
        is_published=False,
        created_by_id=current_user.id
    )

    db.add(new_template)
    db.flush()

    # Create form fields
    for idx, field_data in enumerate(template.fields):
        field = FormField(
            template_id=new_template.id,
            field_name=field_data.field_name,
            field_label=field_data.field_label,
            field_type=field_data.field_type,
            is_required=field_data.is_required,
            options=field_data.options,
            order=idx,
            created_by_id=current_user.id
        )
        db.add(field)

    db.commit()
    db.refresh(new_template)

    return {
        "message": "Form template created successfully",
        "template_id": new_template.id,
        "code": new_template.code
    }


@router.get("/templates", response_model=List[dict])
async def list_form_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all form templates"""
    templates = db.query(FormTemplate).filter(
        FormTemplate.is_deleted == False
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "category": t.category,
            "is_published": t.is_published
        }
        for t in templates
    ]


@router.post("/records", response_model=dict)
async def submit_form_record(
    record_data: FormRecordSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a new form record"""
    template = db.query(FormTemplate).filter(
        FormTemplate.id == record_data.template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found"
        )

    # Generate record number
    year = datetime.now().year
    count = db.query(FormRecord).filter(
        FormRecord.template_id == template.id
    ).count() + 1
    record_number = f"{template.code}-{year}-{count:04d}"

    new_record = FormRecord(
        template_id=template.id,
        record_number=record_number,
        status='draft',
        doer_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_record)
    db.flush()

    # Save form values
    for field_name, value in record_data.values.items():
        form_value = FormValue(
            record_id=new_record.id,
            field_name=field_name,
            value=str(value) if value is not None else None,
            created_by_id=current_user.id
        )
        db.add(form_value)

    db.commit()

    return {
        "message": "Form record submitted successfully",
        "record_id": new_record.id,
        "record_number": record_number
    }


@router.get("/records", response_model=List[dict])
async def list_form_records(
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List form records"""
    query = db.query(FormRecord).filter(FormRecord.is_deleted == False)

    if template_id:
        query = query.filter(FormRecord.template_id == template_id)
    if status:
        query = query.filter(FormRecord.status == status)

    records = query.offset(skip).limit(limit).all()

    return [
        {
            "id": r.id,
            "record_number": r.record_number,
            "template_id": r.template_id,
            "status": r.status,
            "created_at": str(r.created_at)
        }
        for r in records
    ]
