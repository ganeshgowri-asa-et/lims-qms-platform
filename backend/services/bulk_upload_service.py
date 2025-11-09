"""
Bulk Upload Service - Batch upload from Excel/CSV
"""
from typing import Dict, List, Tuple, Any
import pandas as pd
import csv
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    FormTemplate, FormField, BulkUpload, BulkUploadStatusEnum
)
from .record_service import RecordService
from .validation_service import ValidationService


class BulkUploadService:
    """Service for bulk upload operations"""

    def __init__(self, db: Session):
        self.db = db
        self.record_service = RecordService(db)
        self.validation_service = ValidationService(db)

    def process_upload(
        self,
        template_id: int,
        user_id: int,
        file_path: str,
        file_name: str,
        file_type: str
    ) -> Tuple[int, Dict]:
        """Process bulk upload file"""
        # Create bulk upload record
        bulk_upload = BulkUpload(
            template_id=template_id,
            uploaded_by_id=user_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            status=BulkUploadStatusEnum.PENDING
        )
        self.db.add(bulk_upload)
        self.db.commit()

        # Start processing
        bulk_upload.status = BulkUploadStatusEnum.PROCESSING
        bulk_upload.started_at = datetime.utcnow().isoformat()
        self.db.commit()

        try:
            # Read file based on type
            if file_type == "csv":
                data = self._read_csv(file_path)
            elif file_type in ["xlsx", "xls"]:
                data = self._read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            bulk_upload.total_rows = len(data)
            self.db.commit()

            # Get template fields for mapping
            template = self.db.query(FormTemplate).filter_by(id=template_id).first()
            if not template:
                raise ValueError("Template not found")

            fields = {f.field_name: f for f in
                     self.db.query(FormField).filter_by(template_id=template_id).all()}

            # Process each row
            error_log = []
            success_log = []
            validation_errors = []

            for idx, row in enumerate(data, start=1):
                try:
                    # Map row data to field values
                    values = self._map_row_to_values(row, fields)

                    # Validate
                    is_valid, errors, warnings = self.validation_service.validate_record(
                        template_id,
                        values
                    )

                    if not is_valid:
                        validation_errors.append({
                            "row": idx,
                            "errors": errors,
                            "data": row
                        })
                        bulk_upload.failed_rows += 1
                        continue

                    # Create record
                    record = self.record_service.create_record(
                        template_id=template_id,
                        user_id=user_id,
                        values=values,
                        title=row.get("title"),
                        metadata={"bulk_upload_id": bulk_upload.id, "row_number": idx}
                    )

                    success_log.append({
                        "row": idx,
                        "record_id": record.id,
                        "record_number": record.record_number
                    })
                    bulk_upload.successful_rows += 1

                except Exception as e:
                    error_log.append({
                        "row": idx,
                        "error": str(e),
                        "data": row
                    })
                    bulk_upload.failed_rows += 1

                bulk_upload.processed_rows = idx
                if idx % 10 == 0:  # Commit progress every 10 rows
                    self.db.commit()

            # Update bulk upload record
            bulk_upload.status = BulkUploadStatusEnum.COMPLETED if bulk_upload.failed_rows == 0 else BulkUploadStatusEnum.PARTIAL
            bulk_upload.completed_at = datetime.utcnow().isoformat()
            bulk_upload.error_log = error_log
            bulk_upload.success_log = success_log
            bulk_upload.validation_errors = validation_errors
            self.db.commit()

            return bulk_upload.id, {
                "total_rows": bulk_upload.total_rows,
                "successful_rows": bulk_upload.successful_rows,
                "failed_rows": bulk_upload.failed_rows,
                "error_log": error_log[:10],  # First 10 errors
                "validation_errors": validation_errors[:10]
            }

        except Exception as e:
            bulk_upload.status = BulkUploadStatusEnum.FAILED
            bulk_upload.completed_at = datetime.utcnow().isoformat()
            bulk_upload.error_log = [{"error": str(e)}]
            self.db.commit()

            raise

    def _read_csv(self, file_path: str) -> List[Dict]:
        """Read CSV file"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data

    def _read_excel(self, file_path: str) -> List[Dict]:
        """Read Excel file"""
        df = pd.read_excel(file_path)
        # Convert NaN to None
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')

    def _map_row_to_values(self, row: Dict, fields: Dict[str, FormField]) -> Dict[str, Any]:
        """Map CSV/Excel row to form field values"""
        values = {}

        for field_name, field in fields.items():
            # Try exact match first
            if field_name in row:
                values[field_name] = row[field_name]
            # Try field label match
            elif field.field_label in row:
                values[field_name] = row[field.field_label]
            # Try case-insensitive match
            else:
                for key in row.keys():
                    if key.lower() == field_name.lower() or key.lower() == field.field_label.lower():
                        values[field_name] = row[key]
                        break

        return values

    def get_upload_status(self, upload_id: int) -> Dict:
        """Get bulk upload status"""
        upload = self.db.query(BulkUpload).filter_by(id=upload_id).first()
        if not upload:
            raise ValueError("Bulk upload not found")

        return {
            "id": upload.id,
            "file_name": upload.file_name,
            "status": upload.status.value,
            "total_rows": upload.total_rows,
            "processed_rows": upload.processed_rows,
            "successful_rows": upload.successful_rows,
            "failed_rows": upload.failed_rows,
            "started_at": upload.started_at,
            "completed_at": upload.completed_at,
            "error_log": upload.error_log,
            "success_log": upload.success_log,
            "validation_errors": upload.validation_errors
        }

    def generate_template_csv(self, template_id: int) -> str:
        """Generate CSV template with field headers"""
        fields = self.db.query(FormField).filter_by(
            template_id=template_id
        ).order_by(FormField.order).all()

        headers = ["title"]  # Always include title
        headers.extend([f.field_name for f in fields if f.field_type.value != "section"])

        # Create CSV content
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)

        # Add example row with placeholders
        example_row = ["Example Record Title"]
        for field in fields:
            if field.field_type.value == "section":
                continue
            if field.placeholder:
                example_row.append(field.placeholder)
            else:
                example_row.append(f"Example {field.field_label}")

        writer.writerow(example_row)

        return output.getvalue()

    def download_upload_results(self, upload_id: int) -> str:
        """Generate CSV with upload results"""
        upload = self.db.query(BulkUpload).filter_by(id=upload_id).first()
        if not upload:
            raise ValueError("Bulk upload not found")

        import io
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Row", "Status", "Record Number", "Errors"])

        # Write success rows
        for success in upload.success_log or []:
            writer.writerow([
                success.get("row"),
                "Success",
                success.get("record_number"),
                ""
            ])

        # Write error rows
        for error in upload.error_log or []:
            writer.writerow([
                error.get("row"),
                "Failed",
                "",
                error.get("error")
            ])

        # Write validation error rows
        for val_error in upload.validation_errors or []:
            errors_str = "; ".join([e.get("message", "") for e in val_error.get("errors", [])])
            writer.writerow([
                val_error.get("row"),
                "Validation Failed",
                "",
                errors_str
            ])

        return output.getvalue()
