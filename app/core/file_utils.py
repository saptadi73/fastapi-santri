"""File upload utilities."""

import os
import shutil
from uuid import uuid4
from typing import Optional
from fastapi import UploadFile


class FileUploader:
    """Handle file uploads."""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def get_upload_dir(subfolder: str = "") -> str:
        """Get upload directory path."""
        base_dir = os.path.join("uploads", subfolder) if subfolder else "uploads"
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    @staticmethod
    def validate_image(file: UploadFile) -> tuple[bool, Optional[str]]:
        """Validate image file.
        
        Returns:
            (is_valid, error_message)
        """
        if not file:
            return True, None
            
        # Check file extension
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in FileUploader.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed: {', '.join(FileUploader.ALLOWED_EXTENSIONS)}"
        
        return True, None
    
    @staticmethod
    async def save_upload_file(
        file: UploadFile,
        subfolder: str = "",
        prefix: str = ""
    ) -> str:
        """Save uploaded file and return relative path.
        
        Args:
            file: UploadFile object
            subfolder: Subfolder under uploads/
            prefix: Filename prefix
            
        Returns:
            Relative path to saved file (e.g., "uploads/pesantren/abc123.jpg")
        """
        if not file or not file.filename:
            raise ValueError("Uploaded file has no filename")

        # Generate unique filename
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{prefix}{uuid4().hex}{ext}"
        
        # Create directory
        upload_dir = FileUploader.get_upload_dir(subfolder)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return relative path (for database storage)
        return file_path.replace("\\", "/")  # Normalize path separators
    
    @staticmethod
    def delete_file(file_path: Optional[str]) -> bool:
        """Delete file if exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted, False if not exists
        """
        if not file_path:
            return False
            
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        
        return False
