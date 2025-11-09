"""QR code generation utilities for equipment."""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, Any, Optional


def generate_qr_code(
    equipment_data: Dict[str, Any],
    output_path: str,
    size: int = 300,
    add_label: bool = True,
) -> str:
    """
    Generate QR code for equipment with embedded information.

    Args:
        equipment_data: Dictionary containing equipment information
        output_path: Path where QR code image will be saved
        size: Size of the QR code in pixels (default: 300)
        add_label: Whether to add equipment ID label below QR code

    Returns:
        Path to generated QR code image
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create QR code data string
    equipment_id = equipment_data.get("equipment_id", "UNKNOWN")
    name = equipment_data.get("name", "")
    location = equipment_data.get("location", "")
    serial_number = equipment_data.get("serial_number", "")

    # Format QR code data
    qr_data = f"""Equipment ID: {equipment_id}
Name: {name}
Serial: {serial_number}
Location: {location}
"""

    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )

    # Add data
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create styled QR code image
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(31, 71, 136)),
    )

    # Resize to desired size
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Add label if requested
    if add_label:
        # Calculate new image size with label
        label_height = 60
        new_height = size + label_height

        # Create new image with space for label
        new_img = Image.new("RGB", (size, new_height), "white")
        new_img.paste(img, (0, 0))

        # Add text label
        draw = ImageDraw.Draw(new_img)

        try:
            # Try to use a nice font
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw equipment ID
        text = equipment_id
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        text_y = size + 10

        draw.text((text_x, text_y), text, fill=(31, 71, 136), font=font_large)

        # Draw equipment name
        if name:
            text = name[:30]  # Truncate if too long
            bbox = draw.textbbox((0, 0), text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (size - text_width) // 2
            text_y = size + 35

            draw.text((text_x, text_y), text, fill=(100, 100, 100), font=font_small)

        img = new_img

    # Save image
    img.save(output_path, "PNG")

    return output_path


def generate_batch_qr_codes(
    equipment_list: list,
    output_dir: str,
    size: int = 300,
    add_label: bool = True,
) -> list:
    """
    Generate QR codes for multiple equipment items.

    Args:
        equipment_list: List of equipment dictionaries
        output_dir: Directory where QR codes will be saved
        size: Size of each QR code
        add_label: Whether to add labels

    Returns:
        List of paths to generated QR codes
    """
    os.makedirs(output_dir, exist_ok=True)

    generated_paths = []

    for equipment in equipment_list:
        equipment_id = equipment.get("equipment_id", f"EQP-{equipment.get('id', 'UNKNOWN')}")
        filename = f"{equipment_id}.png"
        output_path = os.path.join(output_dir, filename)

        path = generate_qr_code(equipment, output_path, size, add_label)
        generated_paths.append(path)

    return generated_paths


def generate_qr_code_with_logo(
    equipment_data: Dict[str, Any],
    output_path: str,
    logo_path: Optional[str] = None,
    size: int = 300,
) -> str:
    """
    Generate QR code with optional logo in the center.

    Args:
        equipment_data: Dictionary containing equipment information
        output_path: Path where QR code image will be saved
        logo_path: Path to logo image to embed in center
        size: Size of the QR code

    Returns:
        Path to generated QR code image
    """
    # Generate basic QR code first
    qr_path = generate_qr_code(equipment_data, output_path, size, add_label=False)

    # If logo provided, embed it in the center
    if logo_path and os.path.exists(logo_path):
        qr_img = Image.open(qr_path)
        logo = Image.open(logo_path)

        # Calculate logo size (about 20% of QR code)
        logo_size = size // 5
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Create white background for logo
        logo_bg = Image.new("RGB", (logo_size + 10, logo_size + 10), "white")
        logo_bg.paste(logo, (5, 5))

        # Calculate position (center)
        pos = ((size - logo_size - 10) // 2, (size - logo_size - 10) // 2)

        # Paste logo
        qr_img.paste(logo_bg, pos)

        # Save
        qr_img.save(output_path, "PNG")

    return output_path
