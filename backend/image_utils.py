"""
Image utility functions for optimizing and processing images.
"""
import base64
from io import BytesIO
from PIL import Image


def optimize_signature_image(base64_image: str, max_width: int = 600) -> bytes:
    """
    Optimizes a base64-encoded signature image for storage and document generation.

    Args:
        base64_image: Base64-encoded image string (with or without data URI prefix)
        max_width: Maximum width in pixels (default: 600)

    Returns:
        Optimized PNG image as bytes

    Raises:
        Exception: If image format is invalid or processing fails
    """
    try:
        # Handle data URI format (data:image/png;base64,...)
        if ';base64,' in base64_image:
            format_part, imgstr = base64_image.split(';base64,')
            # Validate image format
            if 'image/' not in format_part:
                raise Exception("Invalid image data URI format")
        else:
            # Assume raw base64 string
            imgstr = base64_image

        # Decode base64 to bytes
        image_data = base64.b64decode(imgstr)

        # Open image with PIL
        image = Image.open(BytesIO(image_data))

        # Convert to RGBA to preserve transparency
        # This ensures PNG transparency is maintained
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Resize if image width exceeds max_width
        if image.width > max_width:
            # Calculate new height maintaining aspect ratio
            aspect_ratio = image.height / image.width
            new_width = max_width
            new_height = int(new_width * aspect_ratio)

            # Use LANCZOS for high-quality downsampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save optimized image to bytes
        output = BytesIO()
        image.save(
            output,
            format='PNG',
            optimize=True,  # Enable PNG optimization
            compress_level=6  # Balance between size and speed (0-9)
        )

        # Get the bytes
        optimized_bytes = output.getvalue()
        output.close()

        return optimized_bytes

    except Exception as e:
        raise Exception(f"Failed to optimize signature image: {str(e)}")
