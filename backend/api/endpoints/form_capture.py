"""
Enhanced Form Capture API Endpoints
Comprehensive endpoints for data capture and workflow management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from backend.services.template_parser import TemplateParser
from backend.services.form_generator import FormGenerator
from backend.services.form_data_service import FormDataService
from backend.services.workflow_engine import WorkflowEngine
from backend.services.validation_engine import ValidationEngine, ValidationError
from backend.services.export_service import ExportService
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from pathlib import Path
from fastapi.responses import FileResponse
import os

router = APIRouter()


# Pydantic Models
class TemplateUploadResponse(BaseModel):
    template_id: int
    template_code: str
    template_name: str
    fields_count: int


class FormRecordCreate(BaseModel):
    template_id: int
    title: Optional[str] = None
    form_data: Dict[str, Any]
    auto_submit: bool = False


class FormRecordUpdate(BaseModel):
    form_data: Dict[str, Any]
    partial: bool = True


class WorkflowActionRequest(BaseModel):
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class CheckerReviewRequest(BaseModel):
    approved: bool
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class ApproverReviewRequest(BaseModel):
    approved: bool
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class AssignRequest(BaseModel):
    user_id: int
    comments: Optional[str] = None


# Template Management Endpoints

@router.post("/templates/upload", response_model=TemplateUploadResponse)
async def upload_template_file(
    file: UploadFile = File(...),
    document_id: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse Excel/Word template to create form template

    Supports: .xlsx, .docx, .pdf files
    """
    # Validate file type
    allowed_extensions = ['.xlsx', '.xls', '.docx', '.doc', '.pdf']
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file
    upload_dir = Path("/home/user/lims-qms-platform/uploads/templates")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Parse template
    parser = TemplateParser()

    try:
        if file_ext in ['.xlsx', '.xls']:
            template_data = parser.parse_excel_template(str(file_path))
        elif file_ext in ['.docx', '.doc']:
            template_data = parser.parse_word_template(str(file_path))
        elif file_ext == '.pdf':
            template_data = parser.parse_pdf_template(str(file_path))
        else:
            raise ValueError("Unsupported file type")

        # Update template data
        template_data['source_file'] = str(file_path)
        if category:
            template_data['category'] = category

        # Generate form template
        generator = FormGenerator(db)
        form_template = generator.create_form_from_template_data(
            template_data=template_data,
            document_id=document_id,
            created_by_id=current_user.id
        )

        return TemplateUploadResponse(
            template_id=form_template.id,
            template_code=form_template.code,
            template_name=form_template.name,
            fields_count=len(form_template.fields)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse template: {str(e)}"
        )


@router.get("/templates/{template_id}")
async def get_template_details(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete template definition with fields"""
    from backend.models.form import FormTemplate

    template = db.query(FormTemplate).filter(
        FormTemplate.id == template_id,
        FormTemplate.is_deleted == False
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    fields = [
        {
            'id': f.id,
            'field_name': f.field_name,
            'field_label': f.field_label,
            'field_type': f.field_type.value,
            'is_required': f.is_required,
            'is_readonly': f.is_readonly,
            'placeholder': f.placeholder,
            'help_text': f.help_text,
            'options': f.options,
            'default_value': f.default_value,
            'section': f.section,
            'order': f.order,
            'validation_rules': f.validation_rules
        }
        for f in sorted(template.fields, key=lambda x: x.order)
    ]

    return {
        'id': template.id,
        'name': template.name,
        'code': template.code,
        'description': template.description,
        'category': template.category,
        'version': template.version,
        'is_published': template.is_published,
        'document_id': template.document_id,
        'fields': fields,
        'created_at': str(template.created_at)
    }


@router.post("/templates/{template_id}/publish")
async def publish_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish a template for use"""
    generator = FormGenerator(db)

    try:
        template = generator.publish_template(template_id)
        return {
            'message': 'Template published successfully',
            'template_id': template.id,
            'is_published': template.is_published
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Form Record Endpoints

@router.post("/records", response_model=dict)
async def create_form_record(
    record_data: FormRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new form record"""
    service = FormDataService(db)

    try:
        record = service.create_record(
            template_id=record_data.template_id,
            form_data=record_data.form_data,
            created_by_id=current_user.id,
            title=record_data.title,
            auto_submit=record_data.auto_submit
        )

        return {
            'message': 'Record created successfully',
            'record_id': record.id,
            'record_number': record.record_number,
            'status': record.status
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/records/{record_id}")
async def get_record_details(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete record details with template and workflow history"""
    service = FormDataService(db)

    try:
        return service.get_record_with_template(record_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/records/{record_id}")
async def update_form_record(
    record_id: int,
    update_data: FormRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a form record (draft only)"""
    service = FormDataService(db)

    try:
        record = service.update_record(
            record_id=record_id,
            form_data=update_data.form_data,
            updated_by_id=current_user.id,
            partial=update_data.partial
        )

        return {
            'message': 'Record updated successfully',
            'record_id': record.id,
            'record_number': record.record_number
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a form record (draft only)"""
    service = FormDataService(db)

    try:
        service.delete_record(record_id, current_user.id)
        return {'message': 'Record deleted successfully'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/records")
async def list_records(
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    doer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List form records with filtering"""
    from backend.models.form import FormRecord

    query = db.query(FormRecord).filter(FormRecord.is_deleted == False)

    if template_id:
        query = query.filter(FormRecord.template_id == template_id)
    if status:
        query = query.filter(FormRecord.status == status)
    if doer_id:
        query = query.filter(FormRecord.doer_id == doer_id)

    total = query.count()
    records = query.offset(skip).limit(limit).all()

    return {
        'total': total,
        'records': [
            {
                'id': r.id,
                'record_number': r.record_number,
                'title': r.title,
                'template_id': r.template_id,
                'status': r.status,
                'doer_id': r.doer_id,
                'checker_id': r.checker_id,
                'approver_id': r.approver_id,
                'created_at': str(r.created_at),
                'submitted_at': r.submitted_at
            }
            for r in records
        ]
    }


# Workflow Endpoints

@router.post("/records/{record_id}/submit")
async def submit_record(
    record_id: int,
    action_data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit record for review (Doer action)"""
    service = FormDataService(db)

    try:
        record = service.submit_record(
            record_id=record_id,
            user_id=current_user.id,
            comments=action_data.comments,
            signature_data=action_data.signature_data
        )

        return {
            'message': 'Record submitted successfully',
            'record_id': record.id,
            'status': record.status
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/records/{record_id}/assign-checker")
async def assign_checker(
    record_id: int,
    assign_data: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a checker to review the record"""
    workflow_engine = WorkflowEngine(db)

    try:
        record = workflow_engine.assign_checker(
            record_id=record_id,
            checker_id=assign_data.user_id,
            assigned_by_id=current_user.id,
            comments=assign_data.comments
        )

        return {
            'message': 'Checker assigned successfully',
            'record_id': record.id,
            'checker_id': record.checker_id,
            'status': record.status
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/records/{record_id}/checker-review")
async def checker_review(
    record_id: int,
    review_data: CheckerReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Checker reviews and approves/rejects the record"""
    workflow_engine = WorkflowEngine(db)

    try:
        record = workflow_engine.checker_review(
            record_id=record_id,
            checker_id=current_user.id,
            approved=review_data.approved,
            comments=review_data.comments,
            signature_data=review_data.signature_data
        )

        return {
            'message': f"Record {'approved' if review_data.approved else 'rejected'} by checker",
            'record_id': record.id,
            'status': record.status
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/records/{record_id}/assign-approver")
async def assign_approver(
    record_id: int,
    assign_data: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign an approver for final approval"""
    workflow_engine = WorkflowEngine(db)

    try:
        record = workflow_engine.assign_approver(
            record_id=record_id,
            approver_id=assign_data.user_id,
            assigned_by_id=current_user.id,
            comments=assign_data.comments
        )

        return {
            'message': 'Approver assigned successfully',
            'record_id': record.id,
            'approver_id': record.approver_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/records/{record_id}/approver-review")
async def approver_review(
    record_id: int,
    review_data: ApproverReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approver gives final approval/rejection"""
    workflow_engine = WorkflowEngine(db)

    try:
        record = workflow_engine.approver_review(
            record_id=record_id,
            approver_id=current_user.id,
            approved=review_data.approved,
            comments=review_data.comments,
            signature_data=review_data.signature_data
        )

        return {
            'message': f"Record {'approved' if review_data.approved else 'rejected'}",
            'record_id': record.id,
            'status': record.status
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/records/{record_id}/request-changes")
async def request_changes(
    record_id: int,
    action_data: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request changes to the record"""
    workflow_engine = WorkflowEngine(db)

    if not action_data.comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are required when requesting changes"
        )

    try:
        record = workflow_engine.request_changes(
            record_id=record_id,
            user_id=current_user.id,
            comments=action_data.comments,
            back_to_doer=True
        )

        return {
            'message': 'Changes requested',
            'record_id': record.id,
            'status': record.status
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/records/{record_id}/workflow-history")
async def get_workflow_history(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete workflow history for a record"""
    workflow_engine = WorkflowEngine(db)

    return {
        'record_id': record_id,
        'history': workflow_engine.get_workflow_history(record_id)
    }


# Validation Endpoints

@router.post("/templates/{template_id}/validate")
async def validate_form_data(
    template_id: int,
    form_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate form data without creating a record"""
    validation_engine = ValidationEngine(db)

    errors = validation_engine.validate_form_data(
        template_id=template_id,
        form_data=form_data
    )

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


# Auto-population Endpoints

@router.get("/templates/{template_id}/auto-populate")
async def auto_populate_fields(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get auto-populated field values for a template"""
    service = FormDataService(db)

    try:
        populated_data = service.auto_populate_fields(
            template_id=template_id,
            user_id=current_user.id
        )

        return {
            'template_id': template_id,
            'populated_fields': populated_data
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Statistics Endpoints

@router.get("/templates/{template_id}/statistics")
async def get_template_statistics(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a template's records"""
    service = FormDataService(db)

    return service.get_record_statistics(template_id)


# Export Endpoints

@router.get("/records/{record_id}/export/pdf")
async def export_record_to_pdf(
    record_id: int,
    include_signatures: bool = True,
    include_workflow: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export form record to PDF"""
    export_service = ExportService(db)

    try:
        pdf_path = export_service.export_to_pdf(
            record_id=record_id,
            include_signatures=include_signatures,
            include_workflow=include_workflow
        )

        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=Path(pdf_path).name
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export PDF: {str(e)}"
        )


@router.get("/records/{record_id}/export/excel")
async def export_record_to_excel(
    record_id: int,
    include_workflow: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export form record to Excel"""
    export_service = ExportService(db)

    try:
        excel_path = export_service.export_to_excel(
            record_id=record_id,
            include_workflow=include_workflow
        )

        return FileResponse(
            excel_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=Path(excel_path).name
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export Excel: {str(e)}"
        )


@router.get("/templates/{template_id}/export/excel")
async def export_template_to_excel(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export blank template to Excel for bulk data entry"""
    export_service = ExportService(db)

    try:
        excel_path = export_service.export_template_to_excel(
            template_id=template_id
        )

        return FileResponse(
            excel_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=Path(excel_path).name
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export template: {str(e)}"
        )
