"""
Database Migration Script for Document & Template Management Module
This migration creates/updates all tables for the comprehensive document management system
"""
from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.core.database import Base, engine
from backend.models.document import (
    Document, DocumentVersion, DocumentLevel, DocumentLink,
    DocumentTableOfContents, DocumentResponsibility, DocumentEquipment,
    DocumentKPI, DocumentFlowchart, TemplateCategory, DocumentNumberingSequence
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade():
    """
    Apply migration - Create all document management tables
    """
    logger.info("Starting document management module migration...")

    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        logger.info("✓ All tables created successfully")

        # Initialize default template categories
        initialize_template_categories()

        # Initialize document levels
        initialize_document_levels()

        logger.info("✓ Migration completed successfully!")

    except Exception as e:
        logger.error(f"✗ Migration failed: {str(e)}")
        raise


def initialize_template_categories():
    """Initialize default template categories"""
    from sqlalchemy.orm import Session
    from backend.core.database import SessionLocal

    db = SessionLocal()

    try:
        logger.info("Initializing default template categories...")

        default_categories = [
            {
                "name": "Quality Management Forms",
                "description": "Forms related to quality management system",
                "process_area": "Quality",
                "sort_order": 1
            },
            {
                "name": "Test Protocols",
                "description": "Standard test protocols and procedures",
                "process_area": "Testing",
                "sort_order": 2
            },
            {
                "name": "Calibration Forms",
                "description": "Equipment calibration and verification forms",
                "process_area": "Calibration",
                "sort_order": 3
            },
            {
                "name": "Inspection Checklists",
                "description": "Quality inspection and verification checklists",
                "process_area": "Inspection",
                "sort_order": 4
            },
            {
                "name": "Equipment Forms",
                "description": "Equipment management and maintenance forms",
                "process_area": "Equipment",
                "sort_order": 5
            },
            {
                "name": "Training Records",
                "description": "Training and competency assessment forms",
                "process_area": "Training",
                "sort_order": 6
            },
            {
                "name": "CAPA Forms",
                "description": "Corrective and Preventive Action forms",
                "process_area": "CAPA",
                "sort_order": 7
            },
            {
                "name": "Audit Forms",
                "description": "Internal and external audit templates",
                "process_area": "Audit",
                "sort_order": 8
            },
            {
                "name": "Document Control",
                "description": "Document control and management forms",
                "process_area": "Document Control",
                "sort_order": 9
            },
            {
                "name": "Customer Forms",
                "description": "Customer-related forms and templates",
                "process_area": "Customer Service",
                "sort_order": 10
            }
        ]

        for category_data in default_categories:
            # Check if category already exists
            existing = db.query(TemplateCategory).filter(
                TemplateCategory.name == category_data["name"]
            ).first()

            if not existing:
                category = TemplateCategory(**category_data)
                db.add(category)
                logger.info(f"  + Created category: {category_data['name']}")

        db.commit()
        logger.info("✓ Template categories initialized")

    except Exception as e:
        db.rollback()
        logger.error(f"✗ Failed to initialize template categories: {str(e)}")
        raise
    finally:
        db.close()


def initialize_document_levels():
    """Initialize document level configurations"""
    from sqlalchemy.orm import Session
    from backend.core.database import SessionLocal

    db = SessionLocal()

    try:
        logger.info("Initializing document level configurations...")

        document_levels = [
            {
                "level_number": 1,
                "level_name": "Level 1 - Quality Manual & Policy",
                "description": "Quality Manual, Policy Documents, Vision, Mission",
                "numbering_format": "QM-{year}-{seq:04d}"
            },
            {
                "level_number": 2,
                "level_name": "Level 2 - Quality System Procedures",
                "description": "Quality System Procedures (ISO 17025/9001)",
                "numbering_format": "PROC-{year}-{seq:04d}"
            },
            {
                "level_number": 3,
                "level_name": "Level 3 - Operation & Test Procedures",
                "description": "Operation, Execution, and Test Procedures (PV Standards: IEC 61215, 61730, etc.)",
                "numbering_format": "OP-{year}-{seq:04d}"
            },
            {
                "level_number": 4,
                "level_name": "Level 4 - Templates & Formats",
                "description": "Formats, Templates, Checklists, Test Protocols",
                "numbering_format": "FORM-{year}-{seq:04d}"
            },
            {
                "level_number": 5,
                "level_name": "Level 5 - Records",
                "description": "Records generated from Level 4 templates",
                "numbering_format": "REC-{year}-{seq:04d}"
            }
        ]

        for level_data in document_levels:
            # Check if level already exists
            existing = db.query(DocumentLevel).filter(
                DocumentLevel.level_number == level_data["level_number"]
            ).first()

            if not existing:
                level = DocumentLevel(**level_data)
                db.add(level)
                logger.info(f"  + Created document level: {level_data['level_name']}")

        db.commit()
        logger.info("✓ Document levels initialized")

    except Exception as e:
        db.rollback()
        logger.error(f"✗ Failed to initialize document levels: {str(e)}")
        raise
    finally:
        db.close()


def downgrade():
    """
    Rollback migration - Drop all document management tables
    WARNING: This will delete all data!
    """
    logger.warning("Rolling back document management module migration...")

    try:
        # Drop all tables in reverse order (to handle foreign keys)
        tables_to_drop = [
            'document_flowcharts',
            'document_kpis',
            'document_equipment',
            'document_responsibilities',
            'document_table_of_contents',
            'document_links',
            'document_numbering_sequences',
            'template_categories',
            'document_versions',
            'documents',
            'document_levels'
        ]

        with engine.connect() as conn:
            for table_name in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                    logger.info(f"✓ Dropped table: {table_name}")
                except Exception as e:
                    logger.warning(f"⚠ Could not drop table {table_name}: {str(e)}")

            conn.commit()

        logger.info("✓ Rollback completed")

    except Exception as e:
        logger.error(f"✗ Rollback failed: {str(e)}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        confirmation = input("⚠ WARNING: This will delete all document data! Type 'YES' to confirm: ")
        if confirmation == "YES":
            downgrade()
        else:
            print("Rollback cancelled")
    else:
        upgrade()
