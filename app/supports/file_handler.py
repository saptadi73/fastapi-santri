"""File upload and handling utilities."""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException
from datetime import datetime


class FileHandler:
    """Handler for file upload operations."""
    
    # Default allowed extensions
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}
    ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz"}
    
    def __init__(
        self,
        upload_dir: str = "uploads",
        max_size_mb: int = 10,
        allowed_extensions: Optional[List[str]] = None
    ):
        """
        Initialize file handler.
        
        Args:
            upload_dir: Base directory for uploads
            max_size_mb: Maximum file size in MB
            allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
        """
        self.upload_dir = Path(upload_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_extensions = set(allowed_extensions) if allowed_extensions else None
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def is_allowed_extension(self, filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed, False otherwise
        """
        if not self.allowed_extensions:
            return True
            
        ext = Path(filename).suffix.lower()
        return ext in self.allowed_extensions

    def validate_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file.filename:
            return False, "No filename provided"
        
        # Check extension
        if not self.is_allowed_extension(file.filename):
            allowed = ", ".join(self.allowed_extensions) if self.allowed_extensions else "any"
            return False, f"File type not allowed. Allowed types: {allowed}"
        
        # Check file size if file object has size attribute
        if hasattr(file, "size") and file.size:
            if file.size > self.max_size_bytes:
                max_mb = self.max_size_bytes / (1024 * 1024)
                return False, f"File too large. Maximum size: {max_mb}MB"
        
        return True, None

    def generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """
        Generate unique filename with timestamp and UUID.
        
        Args:
            original_filename: Original filename
            prefix: Optional prefix for the filename
            
        Returns:
            Generated unique filename
        """
        ext = Path(original_filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        return f"{timestamp}_{unique_id}{ext}"

    async def save_file(
        self,
        file: UploadFile,
        subfolder: str = "",
        prefix: str = "",
        custom_filename: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Save uploaded file to disk.
        
        Args:
            file: Uploaded file object
            subfolder: Subfolder within upload directory
            prefix: Prefix for generated filename
            custom_filename: Use custom filename instead of generating one
            
        Returns:
            Tuple of (file_path, filename)
            
        Raises:
            HTTPException: If file validation fails or save operation fails
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Prepare directory
        save_dir = self.upload_dir / subfolder if subfolder else self.upload_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            # file.filename is guaranteed to exist due to validation above
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            filename = self.generate_filename(file.filename, prefix)
        
        file_path = save_dir / filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        finally:
            await file.close()
        
        # Return POSIX-style path to ensure forward slashes for URLs
        return file_path.as_posix(), filename

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from disk.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "filename": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "extension": path.suffix,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except Exception:
            return None


# Convenience functions
def allowed_file(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Check if filename has allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if allowed, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


async def save_upload_file(
    file: UploadFile,
    upload_dir: str = "uploads",
    subfolder: str = "",
    max_size_mb: int = 10,
    allowed_extensions: Optional[List[str]] = None
) -> Tuple[str, str]:
    """
    Quick function to save an uploaded file.
    
    Args:
        file: Uploaded file object
        upload_dir: Base upload directory
        subfolder: Subfolder within upload directory
        max_size_mb: Maximum file size in MB
        allowed_extensions: List of allowed extensions
        
    Returns:
        Tuple of (file_path, filename)
    """
    handler = FileHandler(
        upload_dir=upload_dir,
        max_size_mb=max_size_mb,
        allowed_extensions=allowed_extensions
    )
    return await handler.save_file(file, subfolder=subfolder)


def delete_file(file_path: str) -> bool:
    """
    Quick function to delete a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted, False otherwise
    """
    handler = FileHandler()
    return handler.delete_file(file_path)
