"""
Command-line interface for re-pixel image compression tool
"""

import click
import json
import sys

from .compressor import ImageCompressor
from .utils import find_images_in_directory, format_file_size
from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="repixel")
@click.pass_context
def main(ctx):
    """
    Repixel - A powerful image compression tool

    Compress images with various algorithms and formats while maintaining quality.
    """
    ctx.ensure_object(dict)
    ctx.obj["compressor"] = ImageCompressor()


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option(
    "-q", "--quality", type=int, default=85, help="Compression quality (1-100)"
)
@click.option(
    "-f", "--format", type=click.Choice(["jpeg", "png", "webp"]), help="Output format"
)
@click.option("--optimize/--no-optimize", default=True, help="Enable optimization")
@click.option("--progressive", is_flag=True, help="Enable progressive JPEG")
@click.option("--lossless", is_flag=True, help="Use lossless compression (WebP only)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def compress(
    ctx, input_path, output, quality, format, optimize, progressive, lossless, verbose
):
    """Compress a single image file."""
    compressor = ctx.obj["compressor"]

    try:
        result = compressor.compress(
            input_path=input_path,
            output_path=output,
            quality=quality,
            format=format,
            optimize=optimize,
            progressive=progressive,
            lossless=lossless,
        )

        if result.get("success", True):
            click.echo(f"✅ Compressed: {result['input_path']}")
            click.echo(f"   Output: {result['output_path']}")
            click.echo(f"   Original: {result['original_size_mb']:.2f} MB")
            click.echo(f"   Compressed: {result['compressed_size_mb']:.2f} MB")
            click.echo(f"   Ratio: {result['compression_ratio']:.2%}")
            click.echo(
                f"   Saved: {result['space_saved_mb']:.2f} MB ({result['space_saved_percent']:.1f}%)"
            )

            if verbose:
                click.echo(f"   Format: {result.get('format', 'Unknown')}")
                click.echo(f"   Quality: {result.get('quality', 'N/A')}")
        else:
            click.echo(
                f"❌ Failed to compress {input_path}: {result.get('error', 'Unknown error')}"
            )
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output-dir", type=click.Path(), help="Output directory")
@click.option(
    "-q", "--quality", type=int, default=85, help="Compression quality (1-100)"
)
@click.option(
    "-f", "--format", type=click.Choice(["jpeg", "png", "webp"]), help="Output format"
)
@click.option(
    "-r", "--recursive", is_flag=True, help="Process subdirectories recursively"
)
@click.option("--optimize/--no-optimize", default=True, help="Enable optimization")
@click.option("--progressive", is_flag=True, help="Enable progressive JPEG")
@click.option("--lossless", is_flag=True, help="Use lossless compression (WebP only)")
@click.option("--json-output", type=click.Path(), help="Save results to JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def batch(
    ctx,
    input_dir,
    output_dir,
    quality,
    format,
    recursive,
    optimize,
    progressive,
    lossless,
    json_output,
    verbose,
):
    """Compress multiple images in a directory."""
    compressor = ctx.obj["compressor"]

    try:
        # Find images first to show count
        images = find_images_in_directory(input_dir, recursive=recursive)
        click.echo(f"Found {len(images)} images to process...")

        if len(images) == 0:
            click.echo("No images found in the specified directory.")
            return

        # Progress bar
        with click.progressbar(length=len(images), label="Compressing images") as bar:
            results = compressor.compress_batch(
                input_dir=input_dir,
                output_dir=output_dir,
                quality=quality,
                format=format,
                recursive=recursive,
                optimize=optimize,
                progressive=progressive,
                lossless=lossless,
            )
            bar.update(len(images))

        # Calculate summary statistics
        successful = [r for r in results if r.get("success", True)]
        failed = [r for r in results if not r.get("success", True)]

        total_original_mb = sum(r.get("original_size_mb", 0) for r in successful)
        total_compressed_mb = sum(r.get("compressed_size_mb", 0) for r in successful)
        total_saved_mb = total_original_mb - total_compressed_mb

        # Display summary
        click.echo("\n📊 Batch Compression Summary:")
        click.echo(f"   ✅ Successful: {len(successful)}")
        click.echo(f"   ❌ Failed: {len(failed)}")
        click.echo(f"   📏 Original size: {total_original_mb:.2f} MB")
        click.echo(f"   🗜️  Compressed size: {total_compressed_mb:.2f} MB")
        click.echo(f"   💾 Space saved: {total_saved_mb:.2f} MB")

        if total_original_mb > 0:
            savings_percent = (total_saved_mb / total_original_mb) * 100
            click.echo(f"   📈 Savings: {savings_percent:.1f}%")

        # Show failed files
        if failed and verbose:
            click.echo("\n❌ Failed files:")
            for result in failed:
                click.echo(
                    f"   - {result['input_path']}: {result.get('error', 'Unknown error')}"
                )

        # Save JSON report if requested
        if json_output:
            with open(json_output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"\n📝 Results saved to: {json_output}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "-s", "--target-size", type=float, required=True, help="Target file size in MB"
)
@click.option(
    "-f", "--format", type=click.Choice(["jpeg", "png", "webp"]), help="Output format"
)
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option("--min-quality", type=int, default=10, help="Minimum quality to try")
@click.option("--max-quality", type=int, default=95, help="Maximum quality to try")
@click.pass_context
def optimize(ctx, input_path, target_size, format, output, min_quality, max_quality):
    """Find optimal quality setting for target file size."""
    compressor = ctx.obj["compressor"]

    try:
        click.echo(f"🎯 Finding optimal quality for target size: {target_size} MB")

        result = compressor.optimize_quality(
            input_path=input_path,
            target_size_mb=target_size,
            format=format,
            min_quality=min_quality,
            max_quality=max_quality,
        )

        # If output path specified, save the optimized version
        if output:
            final_result = compressor.compress(
                input_path=input_path,
                output_path=output,
                quality=result["quality"],
                format=format,
            )
            click.echo(f"✅ Optimized image saved: {output}")
            click.echo(f"   Quality used: {final_result['quality']}")
            click.echo(f"   Final size: {final_result['compressed_size_mb']:.2f} MB")
        else:
            click.echo(f"✅ Optimal quality found: {result['quality']}")
            click.echo(f"   Estimated size: {result['compressed_size_mb']:.2f} MB")
            click.echo("   Use --output to save the optimized version")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.pass_context
def info(ctx, input_path):
    """Display detailed information about an image file."""
    from .utils import get_image_info, convert_mode_description

    try:
        info_data = get_image_info(input_path)

        click.echo(f"📷 Image Information: {info_data['file_name']}")
        click.echo(
            f"   📄 File size: {format_file_size(info_data['size_bytes'])} ({info_data['size_mb']} MB)"
        )
        click.echo(
            f"   📐 Dimensions: {info_data['dimensions']} ({info_data['megapixels']} MP)"
        )
        click.echo(f"   🎨 Format: {info_data['format']}")
        click.echo(f"   🌈 Mode: {convert_mode_description(info_data['mode'])}")
        click.echo(f"   🔢 Bit depth: {info_data['bit_depth']} bits")
        click.echo(f"   📏 Aspect ratio: {info_data['aspect_ratio']}:1")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        sys.exit(1)


@main.command()
@click.pass_context
def formats(ctx):
    """List supported image formats."""
    compressor = ctx.obj["compressor"]

    click.echo("🎨 Supported image formats:")
    for fmt in compressor.get_supported_formats():
        click.echo(f"   • {fmt.upper()}")

    click.echo("\n📝 Format details:")
    click.echo("   • JPEG: Lossy compression, good for photos")
    click.echo("   • PNG: Lossless compression, supports transparency")
    click.echo("   • WebP: Modern format with excellent compression")


if __name__ == "__main__":
    main()
