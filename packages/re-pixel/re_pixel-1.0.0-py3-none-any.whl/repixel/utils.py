"""
Utility functions for image processing and validation
"""

from typing import Union, Dict, Any, List
from pathlib import Path
import mimetypes

from PIL import Image


def validate_image(file_path: Union[str, Path]) -> bool:
    """
    Validate if the file is a supported image format.

    Args:
        file_path: Path to the image file

    Returns:
        True if valid image, False otherwise
    """
    file_path = Path(file_path)

    # Check if file exists
    if not file_path.exists():
        return False

    # Check file extension
    supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
    if file_path.suffix.lower() not in supported_extensions:
        return False

    # Try to open with PIL
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def get_image_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get detailed information about an image file.

    Args:
        file_path: Path to the image file

    Returns:
        Dictionary with image information
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file size
    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    # Get image properties
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
            format_name = img.format

            # Calculate megapixels
            megapixels = (width * height) / 1000000

            # Get bit depth
            if hasattr(img, "bits"):
                bit_depth = img.bits
            else:
                bit_depth = 8 if mode in ("L", "P", "RGB") else 16

            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 3),
                "width": width,
                "height": height,
                "dimensions": f"{width}x{height}",
                "megapixels": round(megapixels, 2),
                "mode": mode,
                "format": format_name,
                "bit_depth": bit_depth,
                "aspect_ratio": round(width / height, 2),
            }

    except Exception as e:
        raise ValueError(f"Cannot read image info: {str(e)}")


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculate the compression ratio.

    Args:
        original_size: Original file size in bytes
        compressed_size: Compressed file size in bytes

    Returns:
        Compression ratio (compressed_size / original_size)
    """
    if original_size == 0:
        return 0.0
    return compressed_size / original_size


def find_images_in_directory(
    directory: Union[str, Path], recursive: bool = False
) -> List[Path]:
    """
    Find all image files in a directory.

    Args:
        directory: Directory path to search
        recursive: Search subdirectories recursively

    Returns:
        List of image file paths
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
    image_files = []

    if recursive:
        for ext in image_extensions:
            image_files.extend(directory.rglob(f"*{ext}"))
            image_files.extend(directory.rglob(f"*{ext.upper()}"))
    else:
        for ext in image_extensions:
            image_files.extend(directory.glob(f"*{ext}"))
            image_files.extend(directory.glob(f"*{ext.upper()}"))

    # Filter out invalid images
    valid_images = []
    for img_path in image_files:
        if validate_image(img_path):
            valid_images.append(img_path)

    return sorted(valid_images)


def estimate_optimal_quality(
    file_size_mb: float, target_size_mb: float, current_quality: int = 85
) -> int:
    """
    Estimate optimal quality setting based on file size ratio.

    Args:
        file_size_mb: Current file size in MB
        target_size_mb: Target file size in MB
        current_quality: Current quality setting

    Returns:
        Estimated optimal quality
    """
    if file_size_mb <= target_size_mb:
        return current_quality

    # Simple linear estimation
    ratio = target_size_mb / file_size_mb
    estimated_quality = int(current_quality * ratio)

    # Clamp to reasonable bounds
    return max(10, min(95, estimated_quality))


def create_output_filename(
    input_path: Union[str, Path], suffix: str = "_compressed", output_format: str = None
) -> Path:
    """
    Create output filename based on input filename.

    Args:
        input_path: Input file path
        suffix: Suffix to add to filename
        output_format: Output format extension

    Returns:
        Output file path
    """
    input_path = Path(input_path)

    if output_format:
        if not output_format.startswith("."):
            output_format = f".{output_format}"
        extension = output_format
    else:
        extension = input_path.suffix

    output_name = f"{input_path.stem}{suffix}{extension}"
    return input_path.parent / output_name


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type of a file.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def is_image_file(file_path: Union[str, Path]) -> bool:
    """
    Check if file is an image based on MIME type.

    Args:
        file_path: Path to the file

    Returns:
        True if file is an image
    """
    mime_type = get_mime_type(file_path)
    return mime_type.startswith("image/")


def convert_mode_description(mode: str) -> str:
    """
    Convert PIL image mode to human-readable description.

    Args:
        mode: PIL image mode

    Returns:
        Human-readable description
    """
    mode_descriptions = {
        "1": "Bilevel (1-bit)",
        "L": "Grayscale (8-bit)",
        "P": "Palette (8-bit)",
        "RGB": "RGB (24-bit)",
        "RGBA": "RGB with Alpha (32-bit)",
        "CMYK": "CMYK (32-bit)",
        "YCbCr": "YCbCr (24-bit)",
        "LAB": "LAB (24-bit)",
        "HSV": "HSV (24-bit)",
    }
    return mode_descriptions.get(mode, f"Unknown ({mode})")
