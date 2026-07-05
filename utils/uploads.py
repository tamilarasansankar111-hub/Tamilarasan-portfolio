"""
File upload helpers.

All uploads go to Supabase Storage (not the local filesystem), so
uploaded photos/resumes/certificates/project images are served from
Supabase's CDN and persist independently of the Flask server.
"""
import os
import time
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from database.supabase import get_supabase


def _allowed(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def _unique_name(filename: str) -> str:
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else "bin"
    safe_base = secure_filename(filename.rsplit(".", 1)[0])[:40] or "file"
    return f"{safe_base}-{int(time.time())}-{uuid.uuid4().hex[:8]}.{ext}"


class UploadError(Exception):
    pass


def upload_image(file_storage, bucket: str) -> str:
    """Validate and upload an image file to the given Supabase Storage bucket.
    Returns the public URL."""
    if not file_storage or file_storage.filename == "":
        raise UploadError("No file selected.")
    if not _allowed(file_storage.filename, current_app.config["ALLOWED_IMAGE_EXTENSIONS"]):
        raise UploadError("Unsupported image type. Use PNG, JPG, JPEG, WEBP or GIF.")
    return _upload_to_bucket(file_storage, bucket)


def upload_document(file_storage, bucket: str) -> str:
    """Validate and upload a PDF document (e.g. resume) to Supabase Storage.
    Returns the public URL."""
    if not file_storage or file_storage.filename == "":
        raise UploadError("No file selected.")
    if not _allowed(file_storage.filename, current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"]):
        raise UploadError("Unsupported file type. Please upload a PDF.")
    return _upload_to_bucket(file_storage, bucket)


def _upload_to_bucket(file_storage, bucket: str) -> str:
    supabase = get_supabase()
    path = _unique_name(file_storage.filename)
    file_bytes = file_storage.read()
    content_type = file_storage.mimetype or "application/octet-stream"

    try:
        supabase.storage.from_(bucket).upload(
            path,
            file_bytes,
            {"content-type": content_type, "upsert": "true"},
        )
    except Exception as exc:  # supabase-py raises its own StorageException
        raise UploadError(f"Upload to Supabase Storage failed: {exc}") from exc

    public_url = supabase.storage.from_(bucket).get_public_url(path)
    return public_url
