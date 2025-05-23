# Media Metadata Toolkit

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A powerful Python library for extracting and removing metadata from various media files, including images, PDFs, audio, and video files.

## Features

- 🖼️ **Comprehensive metadata extraction** from multiple file types:
  - Images (JPEG, PNG, GIF, TIFF, BMP, WebP)
  - PDF documents
  - Audio files (MP3, WAV, FLAC, AAC, OGG)
  - Video files (MP4, MOV, AVI, MKV, WebM)
- 🧹 **Metadata removal** for images (with plans to expand to other formats)
- 🌐 **URL support** - Extract metadata directly from web URLs
- 📂 **Batch processing** - Handle directories of files recursively
- 📊 **Multiple output formats** - JSON, plain text, and more
- 📝 **Detailed logging** - File and console logging with configurable levels
- 🛡️ **Robust error handling** - Clear error messages and graceful failure

## Usage

### Command Line Interface

#### Extract metadata from a file:
```bash
python media_metadata.py image.jpg extract
```

#### Extract metadata from a URL:
```bash
python media_metadata.py https://example.com/image.jpg extract --url
```

#### Remove metadata from an image (save to new file):
```bash
python media_metadata.py image.jpg remove --output clean_image.jpg
```

#### Remove metadata from all images in a directory:
```bash
python media_metadata.py ./photos remove --output ./cleaned_photos --recursive
```

#### Full CLI options:
```
usage: media_metadata.py [-h] [-o OUTPUT] [--url] [--in-place] [-r] [--log-file LOG_FILE] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--version]
                         source {extract,remove}

Media Metadata Toolkit - Extract or remove metadata from media files

positional arguments:
  source                File/directory path or URL to process
  {extract,remove}      Operation to perform

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file/directory path
  --url                 Treat source as a URL (for extraction only)
  --in-place            Modify files in place (for removal only)
  -r, --recursive       Process directories recursively
  --log-file LOG_FILE   Path to log file (default: media_metadata.log)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (default: INFO)
  --version             show program's version number and exit
```

### Python API

```python
from media_metadata import MediaMetadataToolkit

# Initialize toolkit
toolkit = MediaMetadataToolkit()

# Extract metadata from a file
metadata = toolkit.process("document.pdf", "extract")
print(metadata)

# Remove metadata from an image
clean_file = toolkit.process("photo.jpg", "remove", output="clean_photo.jpg")

# Process a directory of images
processed_files = toolkit.process("./photos", "remove", output="./cleaned_photos", recursive=True)
```

## Supported Metadata

### Image Files
- EXIF data (including GPS coordinates)
- Image format, size, mode
- Creation/modification dates
- Camera make and model
- Software used
- And more...

### PDF Files
- Document information (author, title, subject)
- Creation/modification dates
- PDF version
- Page count
- XMP metadata
- Encryption status

### Audio/Video Files
- Duration
- Bitrate
- Codec information
- ID3 tags (for audio)
- Creation/modification dates
- And more...

## Output Formats

The toolkit supports multiple output formats:

1. **JSON** (default for API, recommended for programmatic use)
2. **Plain text** (human-readable format)
3. **In-memory dictionaries** (Python API)

## Examples

### Sample JSON Output (extracted from an image)
```json
{
  "file_type": "image",
  "file_path": "/path/to/image.jpg",
  "file_size": 1024000,
  "file_created": "2023-01-01T12:00:00",
  "file_modified": "2023-01-01T12:00:00",
  "format": "JPEG",
  "size": [1920, 1080],
  "mode": "RGB",
  "exif": {
    "DateTime": "2023:01:01 12:00:00",
    "Make": "Camera Manufacturer",
    "Model": "Camera Model",
    "Software": "Adobe Photoshop 24.0",
    "GPSInfo": {
      "GPSLatitude": [34, 4, 12.34],
      "GPSLongitude": [118, 14, 56.78],
      "GPSLatitudeRef": "N",
      "GPSLongitudeRef": "W"
    }
  },
  "gps": {
    "GPSLatitude": "34°4'12.34\" N",
    "GPSLongitude": "118°14'56.78\" W"
  }
}
```

## Error Handling

The toolkit provides detailed error messages for:
- Unsupported file types
- Permission issues
- Network errors (for URL operations)
- Invalid operations
- Corrupt files

All errors inherit from `MediaMetadataError` for easy exception handling.

## Logging

The toolkit logs to both console and file (`media_metadata.log` by default) with timestamps and source information. Log levels can be configured via CLI or API.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**

## Disclaimer (Sumarized)

This software is provided as-is without any warranties. The developers are not responsible for:
- Any misuse of this software
- Data loss resulting from metadata removal
- Privacy violations caused by extracted metadata
- Compatibility issues with specific file formats or environments

Users are responsible for:
- Validating results for critical applications
- Backing up files before metadata removal
- Complying with all applicable laws and regulations regarding metadata handling
