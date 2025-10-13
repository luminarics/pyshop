"""File storage utilities for avatar uploads"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

# Storage configuration
UPLOAD_DIR = Path("uploads/avatars")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.

    Args:
        file: The uploaded file to validate

    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )


async def save_avatar(file: UploadFile, user_id: str) -> str:
    """
    Save avatar file to disk.

    Args:
        file: The uploaded file
        user_id: The user ID (used for filename)

    Returns:
        The relative URL path to the saved file

    Raises:
        HTTPException: If file saving fails
    """
    # Validate file
    validate_image_file(file)

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / filename

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Return URL path
    return f"/uploads/avatars/{filename}"


def delete_avatar(avatar_url: Optional[str]) -> None:
    """
    Delete avatar file from disk.

    Args:
        avatar_url: The URL path to the avatar file
    """
    if not avatar_url:
        return

    try:
        # Extract filename from URL
        filename = Path(avatar_url).name
        file_path = UPLOAD_DIR / filename

        # Delete file if it exists
        if file_path.exists():
            os.remove(file_path)
    except Exception:
        # Silently fail if file deletion fails
        pass
