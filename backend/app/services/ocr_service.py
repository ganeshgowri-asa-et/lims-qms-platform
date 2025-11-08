"""
OCR service for extracting data from calibration certificates
"""
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import cv2
import numpy as np
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import base64
from io import BytesIO
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class OCRService:
    """Service for OCR extraction from calibration certificates"""

    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert PIL image to OpenCV format
        img_array = np.array(image)

        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.medianBlur(processed, 3)

        # Convert back to PIL Image
        return Image.fromarray(processed)

    @staticmethod
    def extract_text_from_image(image: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_image = OCRService.preprocess_image(image)

            # Perform OCR
            text = pytesseract.image_to_string(processed_image, lang="eng")

            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extract text from PDF calibration certificate"""
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes, dpi=300)

            # Extract text from each page
            full_text = ""
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)}")
                page_text = OCRService.extract_text_from_image(image)
                full_text += f"\n--- Page {i + 1} ---\n{page_text}\n"

            return full_text
        except Exception as e:
            logger.error(f"PDF text extraction failed: {str(e)}")
            return ""

    @staticmethod
    def extract_certificate_number(text: str) -> Optional[str]:
        """Extract certificate number from text"""
        patterns = [
            r"Certificate\s+(?:No|Number|#)[\s:]+([A-Z0-9\-/]+)",
            r"Cert\.?\s+(?:No|#)[\s:]+([A-Z0-9\-/]+)",
            r"Certificate[\s:]+([A-Z0-9\-/]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def extract_dates(text: str) -> Dict[str, Optional[date]]:
        """Extract calibration and due dates from text"""
        dates = {"calibration_date": None, "due_date": None}

        # Common date patterns
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY or DD/MM/YYYY
            r"\d{2}-\d{2}-\d{4}",  # DD-MM-YYYY
            r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}",  # DD Month YYYY
        ]

        # Look for calibration date
        cal_patterns = [
            r"(?:Calibration\s+Date|Date\s+of\s+Calibration|Cal\.?\s+Date)[\s:]+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        ]

        for pattern in cal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = OCRService.parse_date(date_str)
                if parsed_date:
                    dates["calibration_date"] = parsed_date
                    break

        # Look for due/validity date
        due_patterns = [
            r"(?:Due\s+Date|Next\s+Calibration|Valid\s+Until|Validity)[\s:]+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        ]

        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = OCRService.parse_date(date_str)
                if parsed_date:
                    dates["due_date"] = parsed_date
                    break

        return dates

    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """Parse date string into date object"""
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%d %b %Y",
            "%d %B %Y",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def extract_equipment_serial(text: str) -> Optional[str]:
        """Extract equipment serial number from text"""
        patterns = [
            r"Serial\s+(?:No|Number|#)[\s:]+([A-Z0-9\-/]+)",
            r"S/N[\s:]+([A-Z0-9\-/]+)",
            r"SN[\s:]+([A-Z0-9\-/]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def extract_uncertainty(text: str) -> Optional[str]:
        """Extract measurement uncertainty from text"""
        patterns = [
            r"Uncertainty[\s:]+([±]?\s*[\d.]+\s*(?:%|ppm|°C|V|A|Ω|Hz)?)",
            r"U\s*=\s*([±]?\s*[\d.]+\s*(?:%|ppm|°C|V|A|Ω|Hz)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def extract_calibration_data(
        file_content: str, file_name: str
    ) -> Dict[str, Any]:
        """
        Main method to extract all data from calibration certificate
        file_content: base64 encoded file content
        file_name: name of the file
        """
        try:
            # Decode base64 content
            file_bytes = base64.b64decode(file_content)

            # Determine file type and extract text
            text = ""
            if file_name.lower().endswith(".pdf"):
                text = OCRService.extract_text_from_pdf(file_bytes)
            elif file_name.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
                image = Image.open(BytesIO(file_bytes))
                text = OCRService.extract_text_from_image(image)
            else:
                logger.warning(f"Unsupported file type: {file_name}")
                return {"error": "Unsupported file type"}

            # Extract data
            certificate_number = OCRService.extract_certificate_number(text)
            dates = OCRService.extract_dates(text)
            equipment_serial = OCRService.extract_equipment_serial(text)
            uncertainty = OCRService.extract_uncertainty(text)

            # Extract calibration points (basic extraction)
            # This would need more sophisticated logic for actual calibration data tables
            calibration_points = []

            # Extract environmental conditions
            environmental_conditions = {}
            temp_match = re.search(
                r"Temperature[\s:]+(\d+\.?\d*)\s*°?C", text, re.IGNORECASE
            )
            if temp_match:
                environmental_conditions["temperature"] = f"{temp_match.group(1)} °C"

            humidity_match = re.search(
                r"Humidity[\s:]+(\d+\.?\d*)\s*%", text, re.IGNORECASE
            )
            if humidity_match:
                environmental_conditions["humidity"] = f"{humidity_match.group(1)} %"

            # Extract standards used
            standards_used = []
            standards_section = re.search(
                r"(?:Standards?\s+Used|Reference\s+Standards?)[\s:]+(.*?)(?:\n\n|$)",
                text,
                re.IGNORECASE | re.DOTALL,
            )
            if standards_section:
                standards_text = standards_section.group(1)
                # Basic extraction - could be improved
                standards_lines = [
                    line.strip()
                    for line in standards_text.split("\n")
                    if line.strip()
                ]
                standards_used = standards_lines[:5]  # Limit to first 5 lines

            return {
                "certificate_number": certificate_number,
                "calibration_date": dates.get("calibration_date"),
                "due_date": dates.get("due_date"),
                "equipment_serial": equipment_serial,
                "uncertainty": uncertainty,
                "calibration_points": calibration_points,
                "environmental_conditions": environmental_conditions,
                "standards_used": standards_used,
                "raw_text": text[:5000],  # Store first 5000 chars of raw text
                "extraction_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to extract calibration data: {str(e)}")
            return {
                "error": str(e),
                "extraction_timestamp": datetime.now().isoformat(),
            }
