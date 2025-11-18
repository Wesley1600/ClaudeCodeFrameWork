#!/usr/bin/env python3
"""
Vision Skill - Image Processing Helper Script

This script provides advanced image processing utilities for the vision skill,
including format conversion, metadata extraction, and batch operations.

Usage:
    python image_processor.py --operation [convert|metadata|batch|resize] --input [path] [options]

Examples:
    # Convert image format
    python image_processor.py --operation convert --input image.png --output image.jpg

    # Extract metadata
    python image_processor.py --operation metadata --input image.jpg

    # Batch process directory
    python image_processor.py --operation batch --input ./images/ --task resize --width 800

    # Resize single image
    python image_processor.py --operation resize --input large.jpg --width 1024 --height 768
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not installed. Install with: pip install Pillow", file=sys.stderr)


class ImageProcessor:
    """Image processing utility class for vision operations."""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)

    def convert_image(self, input_path: Path, output_path: Path, quality: int = 95) -> bool:
        """
        Convert image from one format to another.

        Args:
            input_path: Path to input image
            output_path: Path to output image
            quality: JPEG quality (1-100)

        Returns:
            True if successful, False otherwise
        """
        if not PIL_AVAILABLE:
            print("Error: PIL/Pillow required for conversion", file=sys.stderr)
            return False

        try:
            self.log(f"Converting {input_path} to {output_path}")

            with Image.open(input_path) as img:
                # Convert RGBA to RGB if saving as JPEG
                if output_path.suffix.lower() in {'.jpg', '.jpeg'} and img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = rgb_img

                # Save with appropriate parameters
                save_kwargs = {}
                if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif output_path.suffix.lower() == '.png':
                    save_kwargs['optimize'] = True

                img.save(output_path, **save_kwargs)

            self.log(f"Successfully converted to {output_path}")
            return True

        except Exception as e:
            print(f"Error converting image: {e}", file=sys.stderr)
            return False

    def extract_metadata(self, input_path: Path) -> Dict:
        """
        Extract image metadata including EXIF data.

        Args:
            input_path: Path to input image

        Returns:
            Dictionary containing metadata
        """
        if not PIL_AVAILABLE:
            return {"error": "PIL/Pillow not installed"}

        metadata = {
            "filename": input_path.name,
            "path": str(input_path.absolute()),
            "size_bytes": input_path.stat().st_size,
        }

        try:
            with Image.open(input_path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["size"] = f"{img.width}x{img.height}"

                # Extract EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)

                if exif_data:
                    metadata["exif"] = exif_data

        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    def resize_image(
        self,
        input_path: Path,
        output_path: Path,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> bool:
        """
        Resize an image to specified dimensions.

        Args:
            input_path: Path to input image
            output_path: Path to output image
            width: Target width (None to auto-calculate)
            height: Target height (None to auto-calculate)
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            True if successful, False otherwise
        """
        if not PIL_AVAILABLE:
            print("Error: PIL/Pillow required for resizing", file=sys.stderr)
            return False

        try:
            self.log(f"Resizing {input_path}")

            with Image.open(input_path) as img:
                original_size = img.size

                if maintain_aspect:
                    # Calculate new size maintaining aspect ratio
                    if width and not height:
                        ratio = width / img.width
                        new_size = (width, int(img.height * ratio))
                    elif height and not width:
                        ratio = height / img.height
                        new_size = (int(img.width * ratio), height)
                    elif width and height:
                        # Use thumbnail to maintain aspect within bounds
                        img.thumbnail((width, height), Image.Resampling.LANCZOS)
                        new_size = img.size
                    else:
                        print("Error: Must specify at least width or height", file=sys.stderr)
                        return False
                else:
                    if not width or not height:
                        print("Error: Must specify both width and height when not maintaining aspect", file=sys.stderr)
                        return False
                    new_size = (width, height)

                if new_size != img.size:  # Only resize if thumbnail didn't already
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                img.save(output_path)

            self.log(f"Resized from {original_size} to {new_size}")
            return True

        except Exception as e:
            print(f"Error resizing image: {e}", file=sys.stderr)
            return False

    def batch_process(
        self,
        input_dir: Path,
        task: str,
        output_dir: Optional[Path] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Process multiple images in a directory.

        Args:
            input_dir: Directory containing images
            task: Task to perform (convert, resize, metadata)
            output_dir: Output directory (defaults to input_dir/processed)
            **kwargs: Additional arguments for the task

        Returns:
            List of results for each processed image
        """
        if not input_dir.is_dir():
            print(f"Error: {input_dir} is not a directory", file=sys.stderr)
            return []

        # Find all image files
        image_files = [
            f for f in input_dir.iterdir()
            if f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

        if not image_files:
            print(f"No supported image files found in {input_dir}", file=sys.stderr)
            return []

        self.log(f"Found {len(image_files)} images to process")

        # Set up output directory
        if output_dir is None:
            output_dir = input_dir / "processed"
        output_dir.mkdir(exist_ok=True)

        results = []

        for img_file in image_files:
            result = {
                "input": str(img_file),
                "success": False
            }

            try:
                if task == "metadata":
                    metadata = self.extract_metadata(img_file)
                    result["metadata"] = metadata
                    result["success"] = "error" not in metadata

                elif task == "convert":
                    output_format = kwargs.get('output_format', 'jpg')
                    output_file = output_dir / f"{img_file.stem}.{output_format}"
                    result["success"] = self.convert_image(
                        img_file,
                        output_file,
                        quality=kwargs.get('quality', 95)
                    )
                    result["output"] = str(output_file)

                elif task == "resize":
                    output_file = output_dir / img_file.name
                    result["success"] = self.resize_image(
                        img_file,
                        output_file,
                        width=kwargs.get('width'),
                        height=kwargs.get('height'),
                        maintain_aspect=kwargs.get('maintain_aspect', True)
                    )
                    result["output"] = str(output_file)

                else:
                    result["error"] = f"Unknown task: {task}"

            except Exception as e:
                result["error"] = str(e)

            results.append(result)

        successful = sum(1 for r in results if r["success"])
        self.log(f"Processed {successful}/{len(results)} images successfully")

        return results


def main():
    """Main entry point for the image processor script."""
    parser = argparse.ArgumentParser(
        description="Image processing utilities for vision skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--operation',
        choices=['convert', 'metadata', 'batch', 'resize'],
        required=True,
        help='Operation to perform'
    )

    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input image file or directory'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output file or directory'
    )

    parser.add_argument(
        '--format',
        '--output-format',
        dest='output_format',
        choices=['jpg', 'jpeg', 'png', 'gif', 'webp'],
        default='jpg',
        help='Output format for conversion (default: jpg)'
    )

    parser.add_argument(
        '--quality',
        type=int,
        default=95,
        help='JPEG quality (1-100, default: 95)'
    )

    parser.add_argument(
        '--width',
        type=int,
        help='Target width for resizing'
    )

    parser.add_argument(
        '--height',
        type=int,
        help='Target height for resizing'
    )

    parser.add_argument(
        '--no-aspect',
        action='store_true',
        help='Do not maintain aspect ratio when resizing'
    )

    parser.add_argument(
        '--task',
        choices=['convert', 'resize', 'metadata'],
        help='Task for batch processing'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input path does not exist: {args.input}", file=sys.stderr)
        return 1

    processor = ImageProcessor(verbose=args.verbose)

    # Execute operation
    if args.operation == 'metadata':
        metadata = processor.extract_metadata(args.input)
        if args.json:
            print(json.dumps(metadata, indent=2))
        else:
            print(f"\n=== Metadata for {args.input.name} ===")
            for key, value in metadata.items():
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")

    elif args.operation == 'convert':
        if not args.output:
            args.output = args.input.with_suffix(f'.{args.output_format}')

        success = processor.convert_image(args.input, args.output, args.quality)
        if success:
            print(f"Converted: {args.output}")
            return 0
        else:
            return 1

    elif args.operation == 'resize':
        if not args.output:
            args.output = args.input.parent / f"{args.input.stem}_resized{args.input.suffix}"

        success = processor.resize_image(
            args.input,
            args.output,
            width=args.width,
            height=args.height,
            maintain_aspect=not args.no_aspect
        )

        if success:
            print(f"Resized: {args.output}")
            return 0
        else:
            return 1

    elif args.operation == 'batch':
        if not args.task:
            print("Error: --task required for batch operation", file=sys.stderr)
            return 1

        results = processor.batch_process(
            args.input,
            args.task,
            output_dir=args.output,
            output_format=args.output_format,
            quality=args.quality,
            width=args.width,
            height=args.height,
            maintain_aspect=not args.no_aspect
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            successful = sum(1 for r in results if r["success"])
            print(f"\nProcessed {successful}/{len(results)} images successfully")

            if args.verbose:
                for result in results:
                    status = "✓" if result["success"] else "✗"
                    print(f"{status} {Path(result['input']).name}")

        return 0 if results else 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
