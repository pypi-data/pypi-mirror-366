"""
Re-pixel - A powerful image compression library
"""

__version__ = "1.0.0"
__author__ = "Rakshith Kalmadi"
__email__ = "rakshithkalmadi@gmail.com"

from .compressor import ImageCompressor
from .algorithms import JPEGCompressor, PNGCompressor, WebPCompressor
from .utils import validate_image, get_image_info, calculate_compression_ratio

__all__ = [
    "ImageCompressor",
    "JPEGCompressor",
    "PNGCompressor",
    "WebPCompressor",
    "validate_image",
    "get_image_info",
    "calculate_compression_ratio",
]
