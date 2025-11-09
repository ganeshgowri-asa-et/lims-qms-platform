"""Business logic for Root Cause Analysis."""

from sqlalchemy.orm import Session
from backend.database.models import RootCauseAnalysis, RCAMethod
from backend.api.schemas import RootCauseAnalysisCreate, RootCauseAnalysisUpdate
from typing import List, Optional
import json


class RCAService:
    """Service class for Root Cause Analysis operations."""

    @staticmethod
    def create_rca(db: Session, rca_data: RootCauseAnalysisCreate) -> RootCauseAnalysis:
        """
        Create a new Root Cause Analysis.

        Args:
            db: Database session
            rca_data: RCA creation data

        Returns:
            RootCauseAnalysis: Created RCA record
        """
        rca_dict = rca_data.model_dump(exclude_unset=True)

        # Convert Pydantic models to dict for JSON fields
        if 'five_why_data' in rca_dict and rca_dict['five_why_data']:
            rca_dict['five_why_data'] = [step.model_dump() if hasattr(step, 'model_dump') else step
                                          for step in rca_dict['five_why_data']]

        if 'fishbone_data' in rca_dict and rca_dict['fishbone_data']:
            rca_dict['fishbone_data'] = (rca_dict['fishbone_data'].model_dump()
                                         if hasattr(rca_dict['fishbone_data'], 'model_dump')
                                         else rca_dict['fishbone_data'])

        rca = RootCauseAnalysis(**rca_dict)

        db.add(rca)
        db.commit()
        db.refresh(rca)

        return rca

    @staticmethod
    def get_rca_by_id(db: Session, rca_id: int) -> Optional[RootCauseAnalysis]:
        """Get RCA by ID."""
        return db.query(RootCauseAnalysis).filter(RootCauseAnalysis.id == rca_id).first()

    @staticmethod
    def get_rcas_by_nc(db: Session, nc_id: int) -> List[RootCauseAnalysis]:
        """Get all RCAs for a specific NC."""
        return db.query(RootCauseAnalysis).filter(RootCauseAnalysis.nc_id == nc_id).all()

    @staticmethod
    def update_rca(db: Session, rca_id: int, rca_update: RootCauseAnalysisUpdate) -> Optional[RootCauseAnalysis]:
        """
        Update a Root Cause Analysis.

        Args:
            db: Database session
            rca_id: RCA ID
            rca_update: Update data

        Returns:
            RootCauseAnalysis: Updated RCA record
        """
        rca = RCAService.get_rca_by_id(db, rca_id)
        if not rca:
            return None

        update_data = rca_update.model_dump(exclude_unset=True)

        # Convert Pydantic models to dict for JSON fields
        if 'five_why_data' in update_data and update_data['five_why_data']:
            update_data['five_why_data'] = [step.model_dump() if hasattr(step, 'model_dump') else step
                                             for step in update_data['five_why_data']]

        if 'fishbone_data' in update_data and update_data['fishbone_data']:
            update_data['fishbone_data'] = (update_data['fishbone_data'].model_dump()
                                            if hasattr(update_data['fishbone_data'], 'model_dump')
                                            else update_data['fishbone_data'])

        for field, value in update_data.items():
            setattr(rca, field, value)

        db.commit()
        db.refresh(rca)

        return rca

    @staticmethod
    def approve_rca(db: Session, rca_id: int, approved_by: str, comments: Optional[str] = None) -> Optional[RootCauseAnalysis]:
        """
        Approve a Root Cause Analysis.

        Args:
            db: Database session
            rca_id: RCA ID
            approved_by: Username of approver
            comments: Optional approval comments

        Returns:
            RootCauseAnalysis: Approved RCA record
        """
        from datetime import datetime

        rca = RCAService.get_rca_by_id(db, rca_id)
        if not rca:
            return None

        rca.approved_by = approved_by
        rca.approval_date = datetime.utcnow()
        if comments:
            rca.approval_comments = comments

        db.commit()
        db.refresh(rca)

        return rca

    @staticmethod
    def delete_rca(db: Session, rca_id: int) -> bool:
        """
        Delete a Root Cause Analysis.

        Args:
            db: Database session
            rca_id: RCA ID

        Returns:
            bool: True if deleted, False if not found
        """
        rca = RCAService.get_rca_by_id(db, rca_id)
        if not rca:
            return False

        db.delete(rca)
        db.commit()

        return True

    @staticmethod
    def generate_5why_template() -> List[dict]:
        """Generate a template for 5-Why analysis."""
        return [
            {"level": i, "why": f"Why {i}?", "answer": ""}
            for i in range(1, 6)
        ]

    @staticmethod
    def generate_fishbone_template() -> dict:
        """Generate a template for Fishbone diagram."""
        return {
            "man": [],
            "machine": [],
            "method": [],
            "material": [],
            "measurement": [],
            "environment": []
        }
