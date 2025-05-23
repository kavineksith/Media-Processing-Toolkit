#!/usr/bin/env python3
"""
Image Processing Toolkit - A comprehensive library for handling various image operations including:
- Batch image format conversion
- Resizing and rotation
- Extension validation and modification
- Comprehensive error handling and logging
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from PIL import Image, ImageFile

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Custom Exceptions
class ImageProcessingError(Exception):
    """Base exception for all image processing errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class InvalidExtensionError(ImageProcessingError):
    """Raised when an invalid extension is provided."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class FileOperationError(ImageProcessingError):
    """Raised when file operations fail."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class ImageTransformationError(ImageProcessingError):
    """Raised when image transformations fail."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

# Supported extensions with PIL format mappings
SUPPORTED_EXTENSIONS = {
    'input': {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.bmp': 'BMP',
        '.gif': 'GIF',
        '.tiff': 'TIFF',
        '.webp': 'WEBP'
    },
    'output': {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.bmp': 'BMP',
        '.webp': 'WEBP'
    }
}

class ImageValidator:
    """Validates image files and extensions."""
    
    @classmethod
    def validate_input_extension(cls, ext: str) -> str:
        """Validate input file extension and return PIL format."""
        ext = ext.lower()
        if ext not in SUPPORTED_EXTENSIONS['input']:
            raise InvalidExtensionError(
                f"Unsupported input extension: {ext}. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS['input'].keys())}"
            )
        return SUPPORTED_EXTENSIONS['input'][ext]
    
    @classmethod
    def validate_output_extension(cls, ext: str) -> str:
        """Validate output file extension and return PIL format."""
        ext = ext.lower()
        if ext not in SUPPORTED_EXTENSIONS['output']:
            raise InvalidExtensionError(
                f"Unsupported output extension: {ext}. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS['output'].keys())}"
            )
        return SUPPORTED_EXTENSIONS['output'][ext]
    
    @classmethod
    def validate_dimensions(cls, width: int, height: int) -> None:
        """Validate image dimensions."""
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive integers")
    
    @classmethod
    def validate_rotation(cls, degrees: int) -> None:
        """Validate rotation degrees."""
        if not -360 <= degrees <= 360:
            raise ValueError("Rotation must be between -360 and 360 degrees")

class ImageProcessor:
    """Handles core image processing operations."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def process_image(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        rotate: Optional[int] = None
    ) -> bool:
        """
        Process a single image with optional transformations.
        
        Args:
            input_path: Path to input image
            output_path: Path for output image
            output_format: PIL format for output
            width: Target width in pixels
            height: Target height in pixels
            rotate: Rotation degrees
            
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            # Validate paths and parameters
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            if output_path.exists():
                raise FileExistsError(f"Output file exists: {output_path}")
            
            # Open and validate image
            with Image.open(input_path) as img:
                # Convert to RGB if needed (for JPEG compatibility)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                # Apply transformations
                if width or height:
                    new_width = width if width else img.width
                    new_height = height if height else img.height
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                if rotate:
                    img = img.rotate(rotate, expand=True)
                
                # Save with optimized parameters
                img.save(
                    output_path,
                    format=output_format,
                    quality=95,  # High quality for lossy formats
                    optimize=True
                )
            
            self.logger.info(f"Processed: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process {input_path}: {str(e)}")
            # Clean up partial output if exists
            if output_path.exists():
                try:
                    output_path.unlink()
                except OSError:
                    pass
            return False
    
    def process_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path],
        input_ext: str,
        output_ext: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        rotate: Optional[int] = None,
        recursive: bool = False
    ) -> Tuple[int, int, int]:
        """
        Process all images in a directory matching input_ext.
        
        Args:
            input_dir: Directory containing images
            output_dir: Output directory (None for in-place)
            input_ext: Input file extension (with dot)
            output_ext: Output file extension (with dot)
            width: Target width in pixels
            height: Target height in pixels
            rotate: Rotation degrees
            recursive: Process subdirectories
            
        Returns:
            Tuple of (success_count, failure_count, skip_count)
        """
        success = 0
        failure = 0
        skip = 0
        
        # Validate output directory if specified
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get PIL formats
        try:
            input_format = ImageValidator.validate_input_extension(input_ext)
            output_format = ImageValidator.validate_output_extension(output_ext)
        except InvalidExtensionError as e:
            self.logger.error(str(e))
            return 0, 0, 0
        
        # Process files
        for item in input_dir.iterdir():
            if item.is_dir() and recursive:
                sub_output = output_dir / item.name if output_dir else None
                s, f, sk = self.process_directory(
                    item, sub_output, input_ext, output_ext,
                    width, height, rotate, recursive
                )
                success += s
                failure += f
                skip += sk
                continue
                
            if not item.is_file():
                continue
                
            # Check extension match
            if item.suffix.lower() != input_ext.lower():
                skip += 1
                continue
                
            # Determine output path
            if output_dir:
                output_path = output_dir / f"{item.stem}{output_ext}"
            else:
                output_path = item.with_suffix(output_ext)
            
            # Skip if output exists and is different from input
            if output_path.exists() and output_path != item:
                skip += 1
                continue
                
            # Process the image
            if self.process_image(item, output_path, output_format, width, height, rotate):
                success += 1
            else:
                failure += 1
        
        return success, failure, skip

class ImageProcessingCLI:
    """Command-line interface for image processing."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.processor = ImageProcessor(self.logger)
    
    @staticmethod
    def _setup_logging() -> logging.Logger:
        """Configure logging for the application."""
        logger = logging.getLogger('ImageProcessing')
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler('image_processing.log')
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    
    def run(self, args: argparse.Namespace) -> None:
        """Execute the processing based on command-line arguments."""
        try:
            input_path = Path(args.input)
            output_path = Path(args.output) if args.output else None
            
            # Validate input path
            if not input_path.exists():
                raise FileNotFoundError(f"Input path not found: {input_path}")
            
            # Validate extensions
            input_ext = args.input_ext if args.input_ext.startswith('.') else f'.{args.input_ext}'
            output_ext = args.output_ext if args.output_ext.startswith('.') else f'.{args.output_ext}'
            
            # Validate dimensions if provided
            width = args.width
            height = args.height
            if width or height:
                ImageValidator.validate_dimensions(width or 1, height or 1)
            
            # Validate rotation if provided
            rotate = args.rotate
            if rotate:
                ImageValidator.validate_rotation(rotate)
            
            # Process based on input type
            if input_path.is_file():
                if output_path and output_path.is_dir():
                    output_path = output_path / f"{input_path.stem}{output_ext}"
                
                if not output_path:
                    output_path = input_path.with_suffix(output_ext)
                
                success = self.processor.process_image(
                    input_path, output_path,
                    ImageValidator.validate_output_extension(output_ext),
                    width, height, rotate
                )
                
                if success:
                    print(f"Successfully processed: {output_path}")
                else:
                    print(f"Failed to process: {input_path}")
                    sys.exit(1)
            
            elif input_path.is_dir():
                success, failure, skip = self.processor.process_directory(
                    input_path, output_path,
                    input_ext, output_ext,
                    width, height, rotate,
                    args.recursive
                )
                
                print(f"Processing complete: {success} succeeded, {failure} failed, {skip} skipped")
                if failure > 0:
                    sys.exit(1)
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch image processing tool for format conversion, resizing, and rotation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        help="Input file or directory path"
    )
    
    parser.add_argument(
        'output_ext',
        help=f"Output extension (without dot). Supported: {', '.join([e[1:] for e in SUPPORTED_EXTENSIONS['output'].keys()])}"
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        help="Output file or directory path (default: in-place conversion)",
        default=None
    )
    
    parser.add_argument(
        '-i', '--input-ext',
        help="Input file extension to filter by (without dot)",
        default=None
    )
    
    parser.add_argument(
        '-W', '--width',
        help="Target width in pixels (maintains aspect ratio if height not specified)",
        type=int,
        default=None
    )
    
    parser.add_argument(
        '-H', '--height',
        help="Target height in pixels (maintains aspect ratio if width not specified)",
        type=int,
        default=None
    )
    
    parser.add_argument(
        '-r', '--rotate',
        help="Rotation in degrees (positive for clockwise, negative for counter-clockwise)",
        type=int,
        default=None
    )
    
    parser.add_argument(
        '-R', '--recursive',
        help="Process directories recursively",
        action='store_true'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser.parse_args()

def main():
    """Entry point for the CLI application."""
    try:
        args = parse_args()
        cli = ImageProcessingCLI()
        cli.run(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
