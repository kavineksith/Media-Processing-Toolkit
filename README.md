# Media Processing Toolkit (Images Only)

## 🎨 Overview

A comprehensive suite of tools for processing and analyzing media files, including images, videos, and metadata. Designed for photographers, content creators, and developers working with media assets.

## 🛠️ Tools Included

1. **Media Metadata Toolkit**
   - Extract metadata from images, PDFs, audio, and video files
   - Remove sensitive metadata from files
   - Support for batch processing and URL inputs

2. **Image Processing Toolkit**
   - Batch format conversion (PNG, JPG, WebP, etc.)
   - Resizing with aspect ratio control
   - Rotation and transformation
   - Recursive directory processing

3. **Wallpaper Image Processor**
   - Batch resize images to target resolutions
   - Maintain aspect ratios
   - Parallel processing with progress tracking

## ✨ Key Features

- **Metadata Handling**:
  - Extract EXIF, PDF, audio/video metadata
  - Clean sensitive information from files
  - Multiple output formats (JSON, text)

- **Image Processing**:
  - Format conversion
  - Resizing and rotation
  - Bulk operations
  - Input/output validation

- **Performance**:
  - Parallel processing
  - Progress tracking
  - Comprehensive logging

## 🚀 Usage

### Metadata Extraction
```bash
python media_metadata.py image.jpg extract --output metadata.json
```

### Image Conversion
```bash
python image_toolkit.py ./photos webp -o ./converted -R
```

### Wallpaper Processing
```bash
python image_processor.py
# Follow prompts for input/output directories
```

## ⚙️ Configuration

All tools support:
- Custom output locations
- Batch processing flags
- Logging configuration
- Error handling options

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided **"as is"** without any warranty of any kind. It is intended for educational, personal, or professional use in environments where validation and review are standard.

**Use in production systems is at your own risk.**

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**

**Important:** These tools modify files and metadata. Always:
- Maintain backups of original files
- Verify processing results
- Ensure you have rights to modify files

This software is provided "as is" without warranty. The developers are not responsible for any data loss or unintended modifications. **Use at your own risk.**

**For all tools:**
- Designed for professional and personal use
- Test with sample files before bulk processing
- Users are responsible for complying with copyright laws
- Metadata removal may affect some applications
