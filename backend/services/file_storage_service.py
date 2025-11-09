"""
File Storage Service for document management
Handles file uploads, versioning, and storage
"""
import os
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO
from backend.core.config import settings
import uuid


class FileStorageService:
    """Service for managing file storage with versioning"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or settings.UPLOAD_DIR
        self._ensure_directory_structure()

    def _ensure_directory_structure(self):
        """Create necessary directory structure"""
        directories = [
            'documents',
            'documents/level_1',
            'documents/level_2',
            'documents/level_3',
            'documents/level_4',
            'documents/level_5',
            'documents/templates',
            'documents/versions',
            'documents/temp',
        ]
        for directory in directories:
            path = os.path.join(self.base_path, directory)
            os.makedirs(path, exist_ok=True)

    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def calculate_checksum_from_stream(self, file_stream: BinaryIO) -> str:
        """Calculate SHA-256 checksum from file stream"""
        sha256_hash = hashlib.sha256()
        file_stream.seek(0)
        for byte_block in iter(lambda: file_stream.read(4096), b""):
            sha256_hash.update(byte_block)
        file_stream.seek(0)
        return sha256_hash.hexdigest()

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)

    def generate_file_path(
        self,
        level: str,
        document_number: str,
        version: str,
        filename: str,
        is_template: bool = False
    ) -> str:
        """Generate organized file path for document storage"""
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)

        # Extract file extension
        _, ext = os.path.splitext(safe_filename)

        # Create directory structure: level/year/month/
        year = datetime.now().year
        month = datetime.now().month

        if is_template:
            base_dir = os.path.join(self.base_path, 'documents', 'templates')
        else:
            level_dir = level.lower().replace(' ', '_')
            base_dir = os.path.join(self.base_path, 'documents', level_dir, str(year), f"{month:02d}")

        os.makedirs(base_dir, exist_ok=True)

        # Generate unique filename: document_number_version_timestamp.ext
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{document_number}_v{version}_{timestamp}{ext}"

        return os.path.join(base_dir, new_filename)

    def save_file(
        self,
        file_stream: BinaryIO,
        level: str,
        document_number: str,
        version: str,
        original_filename: str,
        is_template: bool = False
    ) -> dict:
        """
        Save file to storage and return metadata
        Returns: dict with file_path, file_size, checksum
        """
        # Generate file path
        file_path = self.generate_file_path(
            level, document_number, version, original_filename, is_template
        )

        # Save file
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file_stream, f)

        # Calculate metadata
        file_size = self.get_file_size(file_path)
        checksum = self.calculate_checksum(file_path)

        return {
            'file_path': file_path,
            'file_size': file_size,
            'checksum': checksum,
            'file_type': self._get_file_type(original_filename)
        }

    def create_version(
        self,
        source_file_path: str,
        new_version: str,
        document_number: str,
        level: str
    ) -> dict:
        """
        Create a new version of a document
        """
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"Source file not found: {source_file_path}")

        # Get original filename
        original_filename = os.path.basename(source_file_path)

        # Generate new path for version
        version_dir = os.path.join(self.base_path, 'documents', 'versions')
        os.makedirs(version_dir, exist_ok=True)

        year = datetime.now().year
        month = datetime.now().month
        version_subdir = os.path.join(version_dir, str(year), f"{month:02d}")
        os.makedirs(version_subdir, exist_ok=True)

        _, ext = os.path.splitext(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{document_number}_v{new_version}_{timestamp}{ext}"
        new_file_path = os.path.join(version_subdir, new_filename)

        # Copy file
        shutil.copy2(source_file_path, new_file_path)

        # Calculate metadata
        file_size = self.get_file_size(new_file_path)
        checksum = self.calculate_checksum(new_file_path)

        return {
            'file_path': new_file_path,
            'file_size': file_size,
            'checksum': checksum,
            'file_type': self._get_file_type(original_filename)
        }

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file to a new location"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_path)
            os.makedirs(dest_dir, exist_ok=True)

            shutil.move(source_path, destination_path)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file content"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file integrity using checksum"""
        if not os.path.exists(file_path):
            return False

        actual_checksum = self.calculate_checksum(file_path)
        return actual_checksum == expected_checksum

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal and invalid characters"""
        # Remove path components
        filename = os.path.basename(filename)

        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        return filename

    def _get_file_type(self, filename: str) -> str:
        """Extract file type from filename"""
        _, ext = os.path.splitext(filename)
        return ext.lower().replace('.', '') if ext else 'unknown'

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        total_size = 0
        file_count = 0

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    pass

        return {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'base_path': self.base_path
        }

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        temp_dir = os.path.join(self.base_path, 'documents', 'temp')
        if not os.path.exists(temp_dir):
            return

        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up temp file {filename}: {e}")
