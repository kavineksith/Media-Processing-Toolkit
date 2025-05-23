# 🖼️ Image Processing Toolkit

A comprehensive command-line image processing library built with Python and Pillow. This toolkit enables efficient batch conversion, resizing, rotation, and validation of image files with robust error handling and logging.

## 📌 Features

- Batch image format conversion (e.g., PNG to JPG, WebP to BMP)
- Resize images with optional aspect ratio control
- Rotate images between -360 to 360 degrees
- Recursive directory processing
- Extension validation and transformation
- In-place or custom output path support
- Logging to console and file (`image_processing.log`)
- CLI support with helpful flags and version info

## 🚀 Installation

Ensure you have Python 3.10+ and [Pillow](https://python-pillow.org/) installed:

```bash
pip install Pillow
````

Clone or download this repository, and make the script executable:

```bash
chmod +x image_toolkit.py
```

## 🛠️ Usage

Basic command syntax:

```bash
./image_toolkit.py <input_path> <output_ext> [options]
```

### Required arguments:

* `input_path`: Path to input file or directory
* `output_ext`: Desired output file extension (without dot, e.g., `jpg`, `png`, `webp`)

### Optional arguments:

| Option              | Description                                                      |
| ------------------- | ---------------------------------------------------------------- |
| `-o`, `--output`    | Output path (file or directory). Defaults to in-place conversion |
| `-i`, `--input-ext` | Input file extension to filter by (without dot)                  |
| `-W`, `--width`     | Resize to target width in pixels                                 |
| `-H`, `--height`    | Resize to target height in pixels                                |
| `-r`, `--rotate`    | Rotate image in degrees (-360 to 360)                            |
| `-R`, `--recursive` | Process directories recursively                                  |
| `--version`         | Show program version and exit                                    |

## 📄 Examples

### Convert a single PNG to JPEG:

```bash
./image_toolkit.py photo.png jpg
```

### Batch convert `.webp` to `.png` in a directory:

```bash
./image_toolkit.py ./images png -i webp -o ./converted
```

### Resize and rotate images recursively:

```bash
./image_toolkit.py ./gallery jpg -i png -o ./output -W 800 -H 600 -r 90 -R
```

### Convert in-place:

```bash
./image_toolkit.py ./photos jpeg -i jpg
```

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.** While care has been taken to ensure reliable behavior, the user assumes all responsibility for the use and results of this toolkit.

**Always back up your files** before performing batch operations.
