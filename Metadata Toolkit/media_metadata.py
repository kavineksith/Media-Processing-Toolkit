#!/usr/bin/env python3
"""
Media Metadata Toolkit - A comprehensive library for handling metadata operations including:
- Metadata extraction from images, PDFs, audio, and video files
- EXIF data removal from images
- URL-based metadata extraction
- Comprehensive error handling and logging
"""

import os
import sys
import argparse
import logging
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from urllib.parse import urlparse
from datetime import datetime
from dataclasses import dataclass

# Third-party imports (handle with try-except for better error messages)
try:
    from PIL import Image, ImageFile, UnidentifiedImageError
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError as e:
    raise ImportError("Pillow library required for image processing. Install with: pip install pillow") from e

try:
    from pypdf import PdfReader
except ImportError as e:
    raise ImportError("PyPDF2 library required for PDF processing. Install with: pip install pypdf") from e

try:
    from mutagen import File
except ImportError as e:
    raise ImportError("Mutagen library required for audio/video processing. Install with: pip install mutagen") from e

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Custom Exceptions
class MediaMetadataError(Exception):
    """Base exception for all media metadata errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class FileOperationError(MediaMetadataError):
    """Error during file operations."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class NetworkError(MediaMetadataError):
    """Network-related errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class InvalidInputError(MediaMetadataError):
    """Invalid input provided."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class UnsupportedMediaError(MediaMetadataError):
    """Unsupported media type."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class MetadataRemovalError(MediaMetadataError):
    """Error during metadata removal."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

@dataclass
class MediaFileInfo:
    """Dataclass for storing basic file information."""
    path: Path
    size: int
    created: datetime
    modified: datetime
    mime_type: Optional[str] = None

class MediaMetadataLogger:
    """Centralized logging configuration for the toolkit."""
    
    def __init__(self, name: str = "MediaMetadataToolkit", log_file: Optional[Path] = None):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            log_file: Optional path to log file
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file, mode="a")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Handle warnings
        logging.captureWarnings(True)
    
    def set_level(self, level: str) -> None:
        """Set logging level."""
        self.logger.setLevel(level.upper())
    
    def log_operation_start(self, operation: str) -> None:
        """Log the start of an operation."""
        self.logger.info(f"Starting operation: {operation}")
    
    def log_operation_end(self, operation: str, success: bool = True) -> None:
        """Log the end of an operation."""
        status = "completed successfully" if success else "failed"
        self.logger.info(f"Operation {operation} {status}")

class MediaMetadataBase:
    """Base class for metadata operations."""
    
    SUPPORTED_EXTENSIONS: Dict[str, List[str]] = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp", ".webp"],
        "pdf": [".pdf"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "video": [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    }
    
    def __init__(self, logger: MediaMetadataLogger):
        self.logger = logger
        self._file_info: Optional[MediaFileInfo] = None
    
    def _get_file_info(self, file_path: Path) -> MediaFileInfo:
        """Get basic file information."""
        stat = file_path.stat()
        return MediaFileInfo(
            path=file_path,
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def _validate_file(self, file_path: Path, check_read: bool = True, check_write: bool = False) -> None:
        """Validate file path and permissions."""
        if not file_path.exists():
            raise FileOperationError(f"Path does not exist: {file_path}")
        
        if check_read and not os.access(file_path, os.R_OK):
            raise FileOperationError(f"No read permission for: {file_path}")
        
        if check_write and not os.access(file_path, os.W_OK):
            raise FileOperationError(f"No write permission for: {file_path}")
    
    def _get_extension(self, file_path: Union[Path, str]) -> str:
        """Get lowercase file extension with dot."""
        return Path(file_path).suffix.lower()
    
    def _is_supported(self, file_path: Path, media_type: Optional[str] = None) -> bool:
        """Check if file extension is supported."""
        ext = self._get_extension(file_path)
        
        if media_type:
            return ext in self.SUPPORTED_EXTENSIONS.get(media_type, [])
        return any(ext in exts for exts in self.SUPPORTED_EXTENSIONS.values())
    
    def _clean_metadata_dict(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata dictionary by handling empty/special values."""
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                cleaned[key] = "N/A"
            elif isinstance(value, (str, list, dict)) and not value:
                if isinstance(value, str):
                    cleaned[key] = "Empty String"
                elif isinstance(value, list):
                    cleaned[key] = []
                else:
                    cleaned[key] = {}
            elif isinstance(value, bytes):
                try:
                    cleaned[key] = value.decode("utf-8", errors="replace")
                except UnicodeDecodeError:
                    cleaned[key] = "Binary Data"
            else:
                cleaned[key] = value
        return cleaned

class MediaMetadataExtractor(MediaMetadataBase):
    """Extracts metadata from various media files."""
    
    def __init__(self, logger: MediaMetadataLogger):
        super().__init__(logger)
    
    def extract(self, source: Union[Path, str], is_url: bool = False) -> Dict[str, Any]:
        """
        Extract metadata from a file or URL.
        
        Args:
            source: Path or URL to extract from
            is_url: Whether source is a URL
            
        Returns:
            Dictionary of metadata
        """
        try:
            if is_url:
                return self._extract_from_url(source)
            return self._extract_from_file(Path(source))
        except Exception as e:
            self.logger.logger.error(f"Metadata extraction failed: {str(e)}")
            raise MediaMetadataError(f"Metadata extraction failed: {str(e)}") from e
    
    def _extract_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a local file."""
        self._validate_file(file_path)
        self._file_info = self._get_file_info(file_path)
        
        ext = self._get_extension(file_path)
        
        if ext in self.SUPPORTED_EXTENSIONS["image"]:
            return self._extract_image_metadata(file_path)
        elif ext in self.SUPPORTED_EXTENSIONS["pdf"]:
            return self._extract_pdf_metadata(file_path)
        elif ext in self.SUPPORTED_EXTENSIONS["audio"] + self.SUPPORTED_EXTENSIONS["video"]:
            return self._extract_av_metadata(file_path)
        else:
            raise UnsupportedMediaError(f"Unsupported file type: {ext}")
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract metadata from a URL by downloading temporarily."""
        temp_file = self._download_url(url)
        try:
            metadata = self._extract_from_file(temp_file)
            metadata.update({
                "source_url": url,
                "content_type": self._get_url_content_type(url)
            })
            return metadata
        finally:
            try:
                temp_file.unlink()
            except Exception as e:
                self.logger.logger.warning(f"Could not delete temp file: {str(e)}")
    
    def _download_url(self, url: str) -> Path:
        """Download URL content to a temporary file."""
        try:
            response = requests.get(
                url,
                stream=True,
                headers={"User-Agent": "MediaMetadataToolkit/1.0"},
                timeout=30
            )
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get("Content-Type", "").split(";")[0]
            ext = self._get_extension_from_content_type(content_type) or ".tmp"
            
            # Create temp file
            temp_file = Path(f"mmt_temp_{datetime.now().timestamp()}{ext}")
            
            with temp_file.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return temp_file
        except requests.RequestException as e:
            raise NetworkError(f"Failed to download URL: {str(e)}") from e
    
    def _get_url_content_type(self, url: str) -> str:
        """Get content type from URL headers."""
        try:
            response = requests.head(
                url,
                headers={"User-Agent": "MediaMetadataToolkit/1.0"},
                timeout=10,
                allow_redirects=True
            )
            return response.headers.get("Content-Type", "unknown")
        except requests.RequestException:
            return "unknown"
    
    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """Map content type to file extension."""
        mapping = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "application/pdf": ".pdf",
            "audio/mpeg": ".mp3",
            "video/mp4": ".mp4",
            "video/quicktime": ".mov"
        }
        return mapping.get(content_type.lower())
    
    def _extract_image_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files."""
        metadata = {"file_type": "image"}
        metadata.update(self._get_base_metadata())
        
        try:
            with Image.open(image_path) as img:
                metadata.update({
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "info": img.info,
                    "is_animated": getattr(img, "is_animated", False),
                    "frames": getattr(img, "n_frames", 1)
                })
                
                # EXIF data
                exif_data = self._extract_exif_data(img)
                if exif_data:
                    metadata["exif"] = exif_data
                    if "GPSInfo" in exif_data:
                        metadata["gps"] = self._extract_gps_data(exif_data["GPSInfo"])
        
        except UnidentifiedImageError as e:
            raise UnsupportedMediaError(f"Unsupported image format: {image_path}") from e
        except Exception as e:
            raise MediaMetadataError(f"Error processing image: {str(e)}") from e
        
        return self._clean_metadata_dict(metadata)
    
    def _extract_exif_data(self, img: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from image."""
        exif_data = {}
        
        if hasattr(img, "_getexif"):
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    exif_data[tag_name] = value
        
        return exif_data
    
    def _extract_gps_data(self, gps_info: Dict) -> Dict[str, Any]:
        """Extract GPS data from EXIF."""
        gps_data = {}
        
        for key in gps_info:
            tag_name = GPSTAGS.get(key, key)
            gps_data[tag_name] = gps_info[key]
        
        return gps_data
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        metadata = {"file_type": "pdf"}
        metadata.update(self._get_base_metadata())
        
        try:
            with pdf_path.open("rb") as f:
                reader = PdfReader(f)
                
                metadata.update({
                    "pdf_version": reader.metadata.get("/PDF", "N/A"),
                    "pages": len(reader.pages),
                    "author": reader.metadata.get("/Author", "N/A"),
                    "creator": reader.metadata.get("/Creator", "N/A"),
                    "producer": reader.metadata.get("/Producer", "N/A"),
                    "subject": reader.metadata.get("/Subject", "N/A"),
                    "title": reader.metadata.get("/Title", "N/A"),
                    "creation_date": reader.metadata.get("/CreationDate", "N/A"),
                    "modification_date": reader.metadata.get("/ModDate", "N/A"),
                    "encrypted": reader.is_encrypted,
                    "xmp_metadata": self._extract_xmp_metadata(reader)
                })
        
        except Exception as e:
            raise MediaMetadataError(f"Error processing PDF: {str(e)}") from e
        
        return self._clean_metadata_dict(metadata)
    
    def _extract_xmp_metadata(self, reader: PdfReader) -> Dict[str, Any]:
        """Extract XMP metadata from PDF."""
        xmp_data = {}
        
        if hasattr(reader, "xmp_metadata"):
            xmp = reader.xmp_metadata
            if xmp:
                xmp_data = {
                    "dc_creator": getattr(xmp, "dc_creator", "N/A"),
                    "dc_description": getattr(xmp, "dc_description", "N/A"),
                    "dc_title": getattr(xmp, "dc_title", "N/A"),
                    "pdf_keywords": getattr(xmp, "pdf_keywords", "N/A"),
                    "xmp_modify_date": getattr(xmp, "xmp_modify_date", "N/A"),
                    "xmp_create_date": getattr(xmp, "xmp_create_date", "N/A"),
                    "xmp_metadata_date": getattr(xmp, "xmp_metadata_date", "N/A"),
                    "xmp_creator_tool": getattr(xmp, "xmp_creator_tool", "N/A")
                }
        
        return xmp_data
    
    def _extract_av_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from audio/video files."""
        metadata = {"file_type": "audio/video"}
        metadata.update(self._get_base_metadata())
        
        try:
            media_file = File(file_path)
            if not media_file:
                raise UnsupportedMediaError(f"Unsupported audio/video format: {file_path}")
            
            metadata.update({
                "mime_type": media_file.mime[0] if media_file.mime else "N/A",
                "length_seconds": media_file.info.length if hasattr(media_file.info, "length") else "N/A",
                "bitrate": media_file.info.bitrate if hasattr(media_file.info, "bitrate") else "N/A"
            })
            
            if hasattr(media_file, "tags"):
                tags = {}
                for key, value in media_file.tags.items():
                    if isinstance(value, list):
                        tags[key] = [str(v) for v in value]
                    else:
                        tags[key] = str(value)
                metadata["tags"] = tags
        
        except Exception as e:
            raise MediaMetadataError(f"Error processing audio/video: {str(e)}") from e
        
        return self._clean_metadata_dict(metadata)
    
    def _get_base_metadata(self) -> Dict[str, Any]:
        """Get base metadata that applies to all files."""
        if not self._file_info:
            return {}
        
        return {
            "file_path": str(self._file_info.path),
            "file_size": self._file_info.size,
            "file_created": self._file_info.created.isoformat(),
            "file_modified": self._file_info.modified.isoformat()
        }

class MediaMetadataRemover(MediaMetadataBase):
    """Removes metadata from media files (currently focused on images)."""
    
    def __init__(self, logger: MediaMetadataLogger):
        super().__init__(logger)
    
    def remove_metadata(
        self,
        source: Union[Path, str],
        output_path: Optional[Union[Path, str]] = None,
        in_place: bool = False
    ) -> Path:
        """
        Remove metadata from a file.
        
        Args:
            source: Path to source file
            output_path: Optional output path
            in_place: Modify file in place (overwrite original)
            
        Returns:
            Path to processed file
        """
        file_path = Path(source)
        self._validate_file(file_path, check_write=in_place)
        
        if not self._is_supported(file_path, "image"):
            raise UnsupportedMediaError(f"Unsupported file type for metadata removal: {file_path.suffix}")
        
        if in_place and output_path:
            raise InvalidInputError("Cannot specify both output_path and in_place=True")
        
        if in_place:
            output_path = file_path.with_name(f"{file_path.stem}_temp{file_path.suffix}")
            result = self._remove_image_metadata(file_path, output_path)
            try:
                file_path.unlink()
                output_path.rename(file_path)
                return file_path
            except Exception as e:
                raise MetadataRemovalError(f"Failed to replace original file: {str(e)}") from e
        else:
            output_path = Path(output_path) if output_path else \
                file_path.with_name(f"{file_path.stem}_clean{file_path.suffix}")
            return self._remove_image_metadata(file_path, output_path)
    
    def remove_metadata_from_directory(
        self,
        directory: Union[Path, str],
        output_dir: Optional[Union[Path, str]] = None,
        recursive: bool = False
    ) -> List[Path]:
        """
        Remove metadata from all supported files in a directory.
        
        Args:
            directory: Path to directory
            output_dir: Optional output directory
            recursive: Process subdirectories
            
        Returns:
            List of processed file paths
        """
        dir_path = Path(directory)
        self._validate_file(dir_path)
        
        if not dir_path.is_dir():
            raise InvalidInputError(f"Path is not a directory: {dir_path}")
        
        output_path = Path(output_dir) if output_dir else dir_path / "clean_metadata"
        output_path.mkdir(exist_ok=True)
        
        processed_files = []
        
        for item in dir_path.iterdir():
            if item.is_dir() and recursive:
                sub_output = output_path / item.name
                processed_files.extend(
                    self.remove_metadata_from_directory(item, sub_output, recursive)
                )
            elif item.is_file() and self._is_supported(item, "image"):
                try:
                    rel_path = item.relative_to(dir_path) if recursive else item.name
                    dest_path = output_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    result = self.remove_metadata(item, dest_path)
                    processed_files.append(result)
                except Exception as e:
                    self.logger.logger.warning(f"Skipped {item}: {str(e)}")
        
        return processed_files
    
    def _remove_image_metadata(self, input_path: Path, output_path: Path) -> Path:
        """Remove metadata from an image file."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed (for JPEG compatibility)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                
                # Save without EXIF data
                img.save(
                    output_path,
                    quality=95,
                    exif=b'',  # Empty EXIF data
                    **img.info  # Preserve other format-specific info
                )
            
            self.logger.logger.info(f"Metadata removed: {input_path} -> {output_path}")
            return output_path
        
        except UnidentifiedImageError as e:
            raise UnsupportedMediaError(f"Unsupported image format: {input_path}") from e
        except Exception as e:
            raise MetadataRemovalError(f"Error removing metadata: {str(e)}") from e

class MediaMetadataToolkit:
    """Main interface for the media metadata toolkit."""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.logger = MediaMetadataLogger("MediaMetadataToolkit", log_file)
        self.extractor = MediaMetadataExtractor(self.logger)
        self.remover = MediaMetadataRemover(self.logger)
    
    def process(
        self,
        source: Union[Path, str],
        operation: str = "extract",
        output: Optional[Union[Path, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], Path, List[Path]]:
        """
        Process media metadata based on operation.
        
        Args:
            source: File/directory path or URL
            operation: 'extract' or 'remove'
            output: Output path/directory (optional)
            **kwargs: Additional operation-specific arguments
            
        Returns:
            Extracted metadata or path(s) to processed files
        """
        self.logger.log_operation_start(operation)
        
        try:
            if operation == "extract":
                is_url = kwargs.get("is_url", False)
                metadata = self.extractor.extract(source, is_url)
                
                if output:
                    self._save_metadata(metadata, output)
                
                return metadata
            
            elif operation == "remove":
                if kwargs.get("is_url", False):
                    raise InvalidInputError("Cannot remove metadata from URLs directly")
                
                if Path(source).is_dir():
                    recursive = kwargs.get("recursive", False)
                    return self.remover.remove_metadata_from_directory(
                        source, output, recursive
                    )
                else:
                    in_place = kwargs.get("in_place", False)
                    return self.remover.remove_metadata(source, output, in_place)
            
            else:
                raise InvalidInputError(f"Unknown operation: {operation}")
        
        except Exception as e:
            self.logger.log_operation_end(operation, success=False)
            raise
        else:
            self.logger.log_operation_end(operation, success=True)
    
    def _save_metadata(self, metadata: Dict[str, Any], output_path: Union[Path, str]) -> None:
        """Save metadata to a file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with output_path.open("w") as f:
                if output_path.suffix.lower() == ".json":
                    json.dump(metadata, f, indent=2)
                else:
                    for key, value in metadata.items():
                        f.write(f"{key}: {value}\n")
        except Exception as e:
            raise FileOperationError(f"Failed to save metadata: {str(e)}") from e

def main():
    """Command-line interface for the toolkit."""
    parser = argparse.ArgumentParser(
        description="Media Metadata Toolkit - Extract or remove metadata from media files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Main arguments
    parser.add_argument(
        "source",
        help="File/directory path or URL to process"
    )
    
    parser.add_argument(
        "operation",
        choices=["extract", "remove"],
        help="Operation to perform"
    )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        help="Output file/directory path",
        default=None
    )
    
    parser.add_argument(
        "--url",
        action="store_true",
        help="Treat source as a URL (for extraction only)"
    )
    
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Modify files in place (for removal only)"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    
    parser.add_argument(
        "--log-file",
        help="Path to log file",
        default="media_metadata.log"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Media Metadata Toolkit 2.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize toolkit
        toolkit = MediaMetadataToolkit(args.log_file)
        toolkit.logger.set_level(args.log_level)
        
        # Process based on operation
        result = toolkit.process(
            source=args.source,
            operation=args.operation,
            output=args.output,
            is_url=args.url,
            in_place=args.in_place,
            recursive=args.recursive
        )
        
        # Print results for CLI
        if args.operation == "extract" and not args.output:
            print(json.dumps(result, indent=2))
        elif args.operation == "remove":
            if isinstance(result, list):
                print(f"Processed {len(result)} files")
            else:
                print(f"Processed file: {result}")
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except MediaMetadataError as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
