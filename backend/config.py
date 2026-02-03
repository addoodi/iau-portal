"""
Configuration constants for IAU Portal backend.
Includes security settings for file uploads and other configurations.
"""

from pathlib import Path

# ==========================================
# File Upload Security Settings
# ==========================================

# Allowed file extensions for attachments (leave request documents)
ALLOWED_ATTACHMENT_EXTENSIONS = {
    'pdf',   # Adobe PDF documents
    'doc',   # Microsoft Word (legacy)
    'docx',  # Microsoft Word (modern)
    'jpg',   # JPEG images
    'jpeg',  # JPEG images (alternate extension)
    'png',   # PNG images
    'gif'    # GIF images
}

# Maximum attachment file size (10MB in bytes)
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file extensions for signatures (images only)
ALLOWED_SIGNATURE_EXTENSIONS = {
    'png',   # PNG images (recommended for signatures)
    'jpg',   # JPEG images
    'jpeg'   # JPEG images (alternate extension)
}

# Maximum signature file size (500KB in bytes)
MAX_SIGNATURE_SIZE = 500 * 1024  # 500KB

# MIME type mapping for validation
# Maps file extensions to expected MIME types
MIME_TYPE_MAP = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif'
}
