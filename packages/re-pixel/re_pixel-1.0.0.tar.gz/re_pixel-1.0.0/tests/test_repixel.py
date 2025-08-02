"""
Tests for re-pixel image compression library
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np

from repixel import ImageCompressor
from repixel.utils import validate_image, get_image_info, calculate_compression_ratio
from repixel.algorithms import JPEGCompressor, PNGCompressor, WebPCompressor


class TestImageCompressor(unittest.TestCase):
    """Test cases for ImageCompressor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.compressor = ImageCompressor()
        
        # Create a test image
        self.test_image_path = self.temp_dir / "test_image.jpg"
        self.create_test_image(self.test_image_path, (800, 600))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path: Path, size: tuple = (100, 100)):
        """Create a test image file."""
        # Create a random image
        img_array = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(path, "JPEG", quality=95)
    
    def test_compress_single_image(self):
        """Test single image compression."""
        output_path = self.temp_dir / "compressed.jpg"
        
        result = self.compressor.compress(
            input_path=self.test_image_path,
            output_path=output_path,
            quality=80
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertLess(result['compressed_size_mb'], result['original_size_mb'])
    
    def test_compress_with_format_conversion(self):
        """Test compression with format conversion."""
        output_path = self.temp_dir / "converted.webp"
        
        result = self.compressor.compress(
            input_path=self.test_image_path,
            output_path=output_path,
            quality=80,
            format="webp"
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertEqual(result['format'], 'WebP')
    
    def test_batch_compression(self):
        """Test batch compression."""
        # Create multiple test images
        input_dir = self.temp_dir / "input"
        output_dir = self.temp_dir / "output"
        input_dir.mkdir()
        
        for i in range(3):
            img_path = input_dir / f"test_{i}.jpg"
            self.create_test_image(img_path)
        
        results = self.compressor.compress_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            quality=85
        )
        
        self.assertEqual(len(results), 3)
        self.assertTrue(output_dir.exists())
        
        # Check that all compressions were successful
        successful = [r for r in results if r.get('success', True)]
        self.assertEqual(len(successful), 3)
    
    def test_optimize_quality(self):
        """Test quality optimization."""
        # Create a larger test image
        large_image_path = self.temp_dir / "large_test.jpg"
        self.create_test_image(large_image_path, (2000, 1500))
        
        original_info = get_image_info(large_image_path)
        target_size = original_info['size_mb'] * 0.5  # Target 50% of original size
        
        result = self.compressor.optimize_quality(
            input_path=large_image_path,
            target_size_mb=target_size,
            format="jpeg"
        )
        
        self.assertTrue(result.get('success', True))
        self.assertLessEqual(result['compressed_size_mb'], target_size * 1.1)  # Allow 10% margin
    
    def test_supported_formats(self):
        """Test getting supported formats."""
        formats = self.compressor.get_supported_formats()
        
        self.assertIsInstance(formats, list)
        self.assertIn('jpeg', formats)
        self.assertIn('png', formats)
        self.assertIn('webp', formats)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create a test image
        self.test_image_path = self.temp_dir / "test_utils.jpg"
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(self.test_image_path, "JPEG")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_image(self):
        """Test image validation."""
        # Valid image
        self.assertTrue(validate_image(self.test_image_path))
        
        # Non-existent file
        self.assertFalse(validate_image(self.temp_dir / "nonexistent.jpg"))
        
        # Invalid file
        text_file = self.temp_dir / "text.txt"
        text_file.write_text("This is not an image")
        self.assertFalse(validate_image(text_file))
    
    def test_get_image_info(self):
        """Test getting image information."""
        info = get_image_info(self.test_image_path)
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['width'], 100)
        self.assertEqual(info['height'], 100)
        self.assertEqual(info['format'], 'JPEG')
        self.assertGreater(info['size_bytes'], 0)
    
    def test_calculate_compression_ratio(self):
        """Test compression ratio calculation."""
        ratio = calculate_compression_ratio(1000, 500)
        self.assertEqual(ratio, 0.5)
        
        ratio = calculate_compression_ratio(0, 100)
        self.assertEqual(ratio, 0.0)


class TestAlgorithms(unittest.TestCase):
    """Test cases for compression algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test images
        self.jpeg_path = self.temp_dir / "test.jpg"
        self.png_path = self.temp_dir / "test.png"
        self.webp_path = self.temp_dir / "test.webp"
        
        # Create test image
        img_array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(self.jpeg_path, "JPEG")
        img.save(self.png_path, "PNG")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_jpeg_compressor(self):
        """Test JPEG compression."""
        compressor = JPEGCompressor()
        output_path = self.temp_dir / "compressed.jpg"
        
        result = compressor.compress(
            self.jpeg_path,
            output_path,
            quality=80,
            optimize=True,
            progressive=True
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertEqual(result['format'], 'JPEG')
    
    def test_png_compressor(self):
        """Test PNG compression."""
        compressor = PNGCompressor()
        output_path = self.temp_dir / "compressed.png"
        
        result = compressor.compress(
            self.png_path,
            output_path,
            quality=85,
            compress_level=6
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertEqual(result['format'], 'PNG')
    
    def test_webp_compressor(self):
        """Test WebP compression."""
        compressor = WebPCompressor()
        output_path = self.temp_dir / "compressed.webp"
        
        result = compressor.compress(
            self.jpeg_path,
            output_path,
            quality=85,
            method=4
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertEqual(result['format'], 'WebP')
    
    def test_webp_lossless(self):
        """Test WebP lossless compression."""
        compressor = WebPCompressor()
        output_path = self.temp_dir / "lossless.webp"
        
        result = compressor.compress(
            self.png_path,
            output_path,
            quality=100,
            lossless=True
        )
        
        self.assertTrue(result.get('success', True))
        self.assertTrue(output_path.exists())
        self.assertTrue(result['lossless'])


if __name__ == '__main__':
    unittest.main()
