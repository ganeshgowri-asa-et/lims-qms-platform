"""
Quote automation service for test requests
"""
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.test_request import TestRequest
from app.models.test_parameter import TestParameter
from app.services.numbering import NumberingService


class QuoteService:
    """Service for automated quote generation"""

    # Predefined pricing for common test parameters
    PARAMETER_PRICING = {
        # Chemical Analysis
        "pH": Decimal("500.00"),
        "Moisture Content": Decimal("800.00"),
        "Ash Content": Decimal("1000.00"),
        "Heavy Metals": Decimal("2500.00"),
        "Solubility": Decimal("1500.00"),

        # Microbiological Testing
        "Total Plate Count": Decimal("1200.00"),
        "Yeast and Mold": Decimal("1500.00"),
        "E.coli": Decimal("1800.00"),
        "Salmonella": Decimal("2000.00"),

        # Physical Testing
        "Hardness": Decimal("800.00"),
        "Tensile Strength": Decimal("1500.00"),
        "Compression": Decimal("1200.00"),
        "Impact Test": Decimal("1800.00"),

        # Environmental
        "Temperature Cycling": Decimal("5000.00"),
        "Humidity Test": Decimal("4000.00"),
        "Salt Spray": Decimal("3500.00"),
    }

    # Priority-based multipliers
    PRIORITY_MULTIPLIER = {
        "low": Decimal("1.0"),
        "medium": Decimal("1.2"),
        "high": Decimal("1.5"),
        "urgent": Decimal("2.0"),
    }

    @staticmethod
    def calculate_parameter_price(
        parameter_name: str,
        quantity: int = 1,
        priority: str = "medium"
    ) -> Decimal:
        """
        Calculate price for a single test parameter

        Args:
            parameter_name: Name of the test parameter
            quantity: Number of tests
            priority: Priority level

        Returns:
            Total price for the parameter
        """
        # Get base price
        base_price = QuoteService.PARAMETER_PRICING.get(
            parameter_name,
            Decimal("1000.00")  # Default price if not found
        )

        # Apply priority multiplier
        multiplier = QuoteService.PRIORITY_MULTIPLIER.get(
            priority.lower(),
            Decimal("1.0")
        )

        # Calculate total
        total = base_price * quantity * multiplier

        return round(total, 2)

    @staticmethod
    def generate_quote(db: Session, test_request_id: int) -> dict:
        """
        Generate automated quote for a test request

        Args:
            db: Database session
            test_request_id: Test request ID

        Returns:
            Dictionary with quote details
        """
        # Get test request
        test_request = db.query(TestRequest).filter(
            TestRequest.id == test_request_id
        ).first()

        if not test_request:
            raise ValueError(f"Test request {test_request_id} not found")

        # Get all test parameters
        parameters = db.query(TestParameter).filter(
            TestParameter.test_request_id == test_request_id
        ).all()

        # Calculate prices for each parameter
        total_amount = Decimal("0.00")
        parameter_details = []

        for param in parameters:
            unit_price = QuoteService.calculate_parameter_price(
                param.parameter_name,
                quantity=1,
                priority=test_request.priority
            )
            quantity = param.quantity if param.quantity else 1
            total_price = unit_price * quantity

            # Update parameter with pricing
            param.unit_price = unit_price
            param.quantity = quantity
            param.total_price = total_price

            total_amount += total_price

            parameter_details.append({
                "parameter_name": param.parameter_name,
                "unit_price": float(unit_price),
                "quantity": quantity,
                "total_price": float(total_price)
            })

        # Generate quote number if not exists
        if not test_request.quote_number:
            quote_number = NumberingService.generate_quote_number(db)
            test_request.quote_number = quote_number
            test_request.quote_amount = total_amount
            test_request.quote_required = True

        db.commit()

        return {
            "quote_number": test_request.quote_number,
            "trq_number": test_request.trq_number,
            "project_name": test_request.project_name,
            "total_amount": float(total_amount),
            "priority": test_request.priority,
            "parameters": parameter_details,
            "generated_date": datetime.now().isoformat()
        }

    @staticmethod
    def approve_quote(
        db: Session,
        test_request_id: int,
        approved_by: str
    ) -> bool:
        """
        Approve a quote for a test request

        Args:
            db: Database session
            test_request_id: Test request ID
            approved_by: Person approving the quote

        Returns:
            True if successful
        """
        test_request = db.query(TestRequest).filter(
            TestRequest.id == test_request_id
        ).first()

        if not test_request:
            return False

        test_request.quote_approved = True
        test_request.quote_approved_by = approved_by
        test_request.quote_approved_date = date.today()

        db.commit()

        return True

    @staticmethod
    def get_quote_summary(db: Session, test_request_id: int) -> dict:
        """
        Get quote summary for a test request

        Args:
            db: Database session
            test_request_id: Test request ID

        Returns:
            Quote summary dictionary
        """
        test_request = db.query(TestRequest).filter(
            TestRequest.id == test_request_id
        ).first()

        if not test_request:
            return {}

        return {
            "quote_number": test_request.quote_number,
            "quote_amount": float(test_request.quote_amount) if test_request.quote_amount else 0.0,
            "quote_approved": test_request.quote_approved,
            "quote_approved_by": test_request.quote_approved_by,
            "quote_approved_date": test_request.quote_approved_date.isoformat() if test_request.quote_approved_date else None
        }
