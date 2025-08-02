"""
Compression algorithms for different image formats
"""

from abc import ABC, abstractmethod
from typing import Union, Dict, Any
from pathlib import Path
import logging

import cv2
import numpy as np
from PIL import Image, ImageEnhance

logger = logging.getLogger(__name__)


class BaseCompressor(ABC):
    """Base class for image compressors."""

    @abstractmethod
    def compress(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        quality: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Compress an image file."""
        pass


class JPEGCompressor(BaseCompressor):
    """JPEG compression with various optimization options."""

    def compress(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        quality: int = 85,
        optimize: bool = True,
        progressive: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Compress image to JPEG format.

        Args:
            input_path: Input image path
            output_path: Output image path
            quality: JPEG quality (1-100)
            optimize: Enable JPEG optimization
            progressive: Enable progressive JPEG

        Returns:
            Compression result dictionary
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    # Create white background for transparency
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img,
                        mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None,
                    )
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Apply additional optimizations if specified
                if kwargs.get("enhance_sharpness"):
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(kwargs.get("sharpness_factor", 1.2))

                if kwargs.get("enhance_contrast"):
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(kwargs.get("contrast_factor", 1.1))

                # Save with JPEG compression
                save_kwargs = {
                    "format": "JPEG",
                    "quality": quality,
                    "optimize": optimize,
                    "progressive": progressive,
                }

                img.save(output_path, **save_kwargs)

                return {
                    "success": True,
                    "format": "JPEG",
                    "quality": quality,
                    "optimize": optimize,
                    "progressive": progressive,
                }

        except Exception as e:
            logger.error(f"JPEG compression failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": "JPEG",
            }


class PNGCompressor(BaseCompressor):
    """PNG compression with various optimization levels."""

    def compress(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        quality: int = 85,
        compress_level: int = 6,
        optimize: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Compress image to PNG format.

        Args:
            input_path: Input image path
            output_path: Output image path
            quality: Quality level (affects color reduction)
            compress_level: PNG compression level (0-9)
            optimize: Enable PNG optimization

        Returns:
            Compression result dictionary
        """
        try:
            with Image.open(input_path) as img:
                # For PNG, we can apply color palette reduction based on quality
                if quality < 90 and img.mode in ("RGB", "RGBA"):
                    # Reduce colors for better compression
                    colors = max(16, int(256 * (quality / 100)))
                    img = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
                    if img.mode == "P":
                        img = img.convert("RGB")

                # Apply additional processing
                if kwargs.get("remove_alpha") and img.mode == "RGBA":
                    # Remove alpha channel and replace with white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                # Save with PNG compression
                save_kwargs = {
                    "format": "PNG",
                    "compress_level": compress_level,
                    "optimize": optimize,
                }

                img.save(output_path, **save_kwargs)

                return {
                    "success": True,
                    "format": "PNG",
                    "compress_level": compress_level,
                    "optimize": optimize,
                    "quality_applied": quality,
                }

        except Exception as e:
            logger.error(f"PNG compression failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": "PNG",
            }


class WebPCompressor(BaseCompressor):
    """WebP compression with advanced options."""

    def compress(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        quality: int = 85,
        method: int = 4,
        lossless: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Compress image to WebP format.

        Args:
            input_path: Input image path
            output_path: Output image path
            quality: WebP quality (1-100)
            method: Compression method (0-6, higher is slower but better)
            lossless: Use lossless compression

        Returns:
            Compression result dictionary
        """
        try:
            with Image.open(input_path) as img:
                # WebP supports both RGB and RGBA
                if img.mode not in ("RGB", "RGBA"):
                    if img.mode in ("LA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")

                # Prepare save arguments
                save_kwargs = {
                    "format": "WEBP",
                    "quality": quality,
                    "method": method,
                    "lossless": lossless,
                    "optimize": True,
                }

                # Add additional WebP-specific options
                if not lossless:
                    save_kwargs.update(
                        {
                            "save_all": True,
                            "minimize_size": True,
                        }
                    )

                img.save(output_path, **save_kwargs)

                return {
                    "success": True,
                    "format": "WebP",
                    "quality": quality,
                    "method": method,
                    "lossless": lossless,
                }

        except Exception as e:
            logger.error(f"WebP compression failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": "WebP",
            }


class AdvancedCompressor:
    """Advanced compression techniques using OpenCV."""

    @staticmethod
    def compress_with_opencv(
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        quality: int = 85,
        format: str = "JPEG",
    ) -> Dict[str, Any]:
        """
        Compress image using OpenCV with advanced preprocessing.

        Args:
            input_path: Input image path
            output_path: Output image path
            quality: Compression quality
            format: Output format

        Returns:
            Compression result dictionary
        """
        try:
            # Read image
            img = cv2.imread(str(input_path))
            if img is None:
                raise ValueError(f"Could not read image: {input_path}")

            # Apply noise reduction
            img = cv2.bilateralFilter(img, 9, 75, 75)

            # Apply sharpening
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            img = cv2.filter2D(img, -1, kernel)

            # Save with appropriate codec
            if format.upper() == "JPEG":
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encoded_img = cv2.imencode(".jpg", img, encode_param)
            elif format.upper() == "PNG":
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 9 - (quality // 10)]
                result, encoded_img = cv2.imencode(".png", img, encode_param)
            elif format.upper() == "WEBP":
                encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
                result, encoded_img = cv2.imencode(".webp", img, encode_param)
            else:
                raise ValueError(f"Unsupported format: {format}")

            if result:
                # Write to file
                with open(output_path, "wb") as f:
                    f.write(encoded_img.tobytes())

                return {
                    "success": True,
                    "format": format,
                    "quality": quality,
                    "method": "opencv_advanced",
                }
            else:
                raise ValueError("Encoding failed")

        except Exception as e:
            logger.error(f"OpenCV compression failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": format,
                "method": "opencv_advanced",
            }

    @staticmethod
    def resize_and_compress(
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
        format: str = "JPEG",
    ) -> Dict[str, Any]:
        """
        Resize image to fit within max dimensions and compress.

        Args:
            input_path: Input image path
            output_path: Output image path
            max_width: Maximum width
            max_height: Maximum height
            quality: Compression quality
            format: Output format

        Returns:
            Compression result dictionary
        """
        try:
            with Image.open(input_path) as img:
                original_size = img.size

                # Calculate new size maintaining aspect ratio
                ratio = min(max_width / img.width, max_height / img.height)

                if ratio < 1:
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    resized = True
                else:
                    resized = False

                # Apply format-specific compression
                if format.upper() == "JPEG":
                    if img.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(
                            img,
                            mask=(
                                img.split()[-1] if img.mode in ("RGBA", "LA") else None
                            ),
                        )
                        img = background

                    img.save(output_path, format="JPEG", quality=quality, optimize=True)

                elif format.upper() == "PNG":
                    img.save(output_path, format="PNG", optimize=True)

                elif format.upper() == "WEBP":
                    img.save(output_path, format="WEBP", quality=quality, optimize=True)

                return {
                    "success": True,
                    "format": format,
                    "quality": quality,
                    "resized": resized,
                    "original_size": original_size,
                    "new_size": img.size if resized else original_size,
                    "method": "resize_and_compress",
                }

        except Exception as e:
            logger.error(f"Resize and compress failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": format,
                "method": "resize_and_compress",
            }
