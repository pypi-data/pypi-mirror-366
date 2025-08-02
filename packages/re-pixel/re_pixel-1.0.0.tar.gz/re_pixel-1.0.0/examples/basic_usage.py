"""
Example usage of the repixel library
"""

from pathlib import Path
from repixel import ImageCompressor

def basic_compression_example():
    """Basic image compression example."""
    print("=== Basic Compression Example ===")
    
    compressor = ImageCompressor()
    
    # Compress a single image
    try:
        result = compressor.compress(
            input_path="sample_image.jpg",
            output_path="compressed_image.jpg",
            quality=80,
            format="jpeg"
        )
        
        print(f"Compression successful!")
        print(f"Original size: {result['original_size_mb']:.2f} MB")
        print(f"Compressed size: {result['compressed_size_mb']:.2f} MB")
        print(f"Space saved: {result['space_saved_percent']:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def batch_compression_example():
    """Batch compression example."""
    print("\n=== Batch Compression Example ===")
    
    compressor = ImageCompressor()
    
    # Compress all images in a directory
    try:
        results = compressor.compress_batch(
            input_dir="input_images",
            output_dir="output_images",
            quality=85,
            format="webp",
            recursive=True
        )
        
        successful = [r for r in results if r.get('success', True)]
        total_saved = sum(r.get('space_saved_mb', 0) for r in successful)
        
        print(f"Processed {len(results)} images")
        print(f"Total space saved: {total_saved:.2f} MB")
        
    except Exception as e:
        print(f"Error: {e}")


def quality_optimization_example():
    """Quality optimization example."""
    print("\n=== Quality Optimization Example ===")
    
    compressor = ImageCompressor()
    
    try:
        # Find optimal quality for target file size
        result = compressor.optimize_quality(
            input_path="large_image.jpg",
            target_size_mb=1.0,  # Target 1 MB
            format="jpeg"
        )
        
        print(f"Optimal quality: {result['quality']}")
        print(f"Resulting size: {result['compressed_size_mb']:.2f} MB")
        
    except Exception as e:
        print(f"Error: {e}")


def advanced_compression_example():
    """Advanced compression with custom settings."""
    print("\n=== Advanced Compression Example ===")
    
    compressor = ImageCompressor()
    
    try:
        # JPEG with custom settings
        result = compressor.compress(
            input_path="photo.jpg",
            output_path="photo_optimized.jpg",
            quality=90,
            format="jpeg",
            optimize=True,
            progressive=True,
            enhance_sharpness=True,
            sharpness_factor=1.2
        )
        
        print(f"Advanced JPEG compression complete")
        print(f"Compression ratio: {result['compression_ratio']:.2%}")
        
        # WebP lossless compression
        result = compressor.compress(
            input_path="graphic.png",
            output_path="graphic.webp",
            quality=100,
            format="webp",
            lossless=True
        )
        
        print(f"WebP lossless compression complete")
        print(f"Size reduction: {result['space_saved_percent']:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def resize_and_compress_example():
    """Resize and compress example."""
    print("\n=== Resize and Compress Example ===")
    
    from repixel.algorithms import AdvancedCompressor
    
    try:
        result = AdvancedCompressor.resize_and_compress(
            input_path="high_res_image.jpg",
            output_path="web_optimized.jpg",
            max_width=1920,
            max_height=1080,
            quality=85,
            format="jpeg"
        )
        
        if result['resized']:
            print(f"Image resized from {result['original_size']} to {result['new_size']}")
        print(f"Compression complete: {result['compressed_size_mb']:.2f} MB")
        
    except Exception as e:
        print(f"Error: {e}")


def image_info_example():
    """Get image information example."""
    print("\n=== Image Information Example ===")
    
    from repixel.utils import get_image_info, format_file_size
    
    try:
        info = get_image_info("sample_image.jpg")
        
        print(f"File: {info['file_name']}")
        print(f"Size: {format_file_size(info['size_bytes'])}")
        print(f"Dimensions: {info['dimensions']}")
        print(f"Format: {info['format']}")
        print(f"Mode: {info['mode']}")
        print(f"Megapixels: {info['megapixels']} MP")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run examples
    basic_compression_example()
    batch_compression_example()
    quality_optimization_example()
    advanced_compression_example()
    resize_and_compress_example()
    image_info_example()
    
    print("\n=== Example Complete ===")
    print("Check the repixel documentation for more features!")
