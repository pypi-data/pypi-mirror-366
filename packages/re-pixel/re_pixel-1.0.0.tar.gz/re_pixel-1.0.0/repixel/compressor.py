"""
Main image compressor class that handles different compression algorithms
"""

from typing import Union, Optional, Dict, Any, List
from pathlib import Path
import logging

from .algorithms import JPEGCompressor, PNGCompressor, WebPCompressor
from .utils import validate_image, get_image_info, calculate_compression_ratio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageCompressor:
    """
    Main image compression class that supports multiple formats and algorithms.
    """

    def __init__(self):
        self.compressors = {
            "jpeg": JPEGCompressor(),
            "jpg": JPEGCompressor(),
            "png": PNGCompressor(),
            "webp": WebPCompressor(),
        }

    def compress(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        quality: int = 85,
        format: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Compress a single image file.

        Args:
            input_path: Path to input image
            output_path: Path for output image (optional)
            quality: Compression quality (1-100)
            format: Output format ('jpeg', 'png', 'webp')
            **kwargs: Additional compression parameters

        Returns:
            Dictionary with compression results
        """
        input_path = Path(input_path)

        # Validate input
        if not validate_image(input_path):
            raise ValueError(f"Invalid image file: {input_path}")

        # Get original image info
        original_info = get_image_info(input_path)
        logger.info(
            f"Compressing {input_path.name} ({original_info['size_mb']:.2f} MB)"
        )

        # Determine output format
        if format is None:
            format = input_path.suffix.lower().lstrip(".")

        # Set output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed.{format}"
        else:
            output_path = Path(output_path)

        # Get appropriate compressor
        compressor = self.compressors.get(format.lower())
        if compressor is None:
            raise ValueError(f"Unsupported format: {format}")

        # Perform compression
        result = compressor.compress(input_path, output_path, quality, **kwargs)

        # Calculate compression ratio
        compressed_info = get_image_info(output_path)
        compression_ratio = calculate_compression_ratio(
            original_info["size_bytes"], compressed_info["size_bytes"]
        )

        result.update(
            {
                "input_path": str(input_path),
                "output_path": str(output_path),
                "original_size_mb": original_info["size_mb"],
                "compressed_size_mb": compressed_info["size_mb"],
                "compression_ratio": compression_ratio,
                "space_saved_mb": original_info["size_mb"] - compressed_info["size_mb"],
                "space_saved_percent": (1 - compression_ratio) * 100,
            }
        )

        logger.info(f"Compression complete: {compression_ratio:.2%} of original size")
        return result

    def compress_batch(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        quality: int = 85,
        format: Optional[str] = None,
        recursive: bool = False,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Compress multiple images in a directory.

        Args:
            input_dir: Directory containing input images
            output_dir: Directory for output images
            quality: Compression quality (1-100)
            format: Output format ('jpeg', 'png', 'webp')
            recursive: Process subdirectories recursively
            **kwargs: Additional compression parameters

        Returns:
            List of compression results for each image
        """
        input_dir = Path(input_dir)

        if not input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")

        # Set output directory
        if output_dir is None:
            output_dir = input_dir / "compressed"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        # Find image files
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.tiff"]
        image_files = []

        if recursive:
            for pattern in patterns:
                image_files.extend(input_dir.rglob(pattern))
        else:
            for pattern in patterns:
                image_files.extend(input_dir.glob(pattern))

        results = []

        logger.info(f"Found {len(image_files)} images to compress")

        for image_file in image_files:
            try:
                # Maintain directory structure if recursive
                if recursive:
                    relative_path = image_file.relative_to(input_dir)
                    output_path = (
                        output_dir
                        / relative_path.parent
                        / f"{relative_path.stem}_compressed.{format or relative_path.suffix.lstrip('.')}"
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = (
                        output_dir
                        / f"{image_file.stem}_compressed.{format or image_file.suffix.lstrip('.')}"
                    )

                result = self.compress(
                    image_file, output_path, quality=quality, format=format, **kwargs
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to compress {image_file.name}: {str(e)}")
                results.append(
                    {"input_path": str(image_file), "error": str(e), "success": False}
                )

        # Summary statistics
        successful = [r for r in results if r.get("success", True)]
        total_original_mb = sum(r.get("original_size_mb", 0) for r in successful)
        total_compressed_mb = sum(r.get("compressed_size_mb", 0) for r in successful)

        logger.info("Batch compression complete:")
        logger.info(f"  - Processed: {len(successful)}/{len(results)} images")
        logger.info(f"  - Original size: {total_original_mb:.2f} MB")
        logger.info(f"  - Compressed size: {total_compressed_mb:.2f} MB")
        logger.info(
            f"  - Space saved: {total_original_mb - total_compressed_mb:.2f} MB"
        )

        return results

    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return list(self.compressors.keys())

    def optimize_quality(
        self,
        input_path: Union[str, Path],
        target_size_mb: float,
        format: Optional[str] = None,
        min_quality: int = 10,
        max_quality: int = 95,
    ) -> Dict[str, Any]:
        """
        Find optimal quality setting to achieve target file size.

        Args:
            input_path: Path to input image
            target_size_mb: Target file size in MB
            format: Output format
            min_quality: Minimum quality to try
            max_quality: Maximum quality to try

        Returns:
            Compression result with optimal quality
        """
        input_path = Path(input_path)

        # Binary search for optimal quality
        low, high = min_quality, max_quality
        best_result = None

        while low <= high:
            mid_quality = (low + high) // 2

            # Create temporary file
            temp_output = (
                input_path.parent
                / f"temp_optimize_{input_path.stem}.{format or input_path.suffix.lstrip('.')}"
            )

            try:
                result = self.compress(
                    input_path, temp_output, quality=mid_quality, format=format
                )

                if result["compressed_size_mb"] <= target_size_mb:
                    best_result = result
                    low = mid_quality + 1
                else:
                    high = mid_quality - 1

            finally:
                # Clean up temp file
                if temp_output.exists():
                    temp_output.unlink()

        if best_result is None:
            raise ValueError(
                f"Cannot achieve target size {target_size_mb} MB with quality range {min_quality}-{max_quality}"
            )

        return best_result
