# Image Processor for Wallpapers

## 📸 Introduction

**Image Processor** is a Python tool designed to batch-process images from a specified input directory. It resizes images to a target resolution while maintaining their aspect ratio. The processed images are saved in an output directory with filenames in the format `wallpaper - 001.jpg`.

This script is useful for preparing wallpapers, compressing image libraries for uniform display, or scaling content for devices like digital frames or presentations.


## 🚀 Usage

### ⚙️ Requirements

* Python 3.10+
* Required libraries:

  * `Pillow`
  * `tqdm`

You can install the required dependencies with:

```bash
pip install pillow tqdm
```

### 🛠️ Running the Script

Run the script via command line or any Python IDE:

```bash
python image_processor.py
```

### 👇 Prompts

You will be prompted to enter:

* **Input directory path** – Directory containing original images.
* **Output directory path** – Where resized images will be saved (defaults to `output`).
* The script appends a timestamp to the output folder to avoid overwriting.

### 🧠 Features

* Supports formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`.
* Deduplicates images based on path (case-insensitive).
* Maintains original aspect ratio (resizes based on width or height).
* Processes images in parallel using up to 4 worker threads.
* Logs events to `image_processor.log` in the output directory.
* Displays a progress bar using `tqdm`.

### 📄 Output Example

```bash
Enter input directory path: ./images
Enter output directory path (default: 'output'): wallpapers
Initializing image processor...
Processing images using 4 worker threads
Processing images: 100%|█████████████████████| 20/20 [00:03<00:00, 6.21img/s]

Processing Summary:
Total images: 20
Successfully processed: 20
Failed: 0
Output directory: wallpapers_20250522_142315
```

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided **"as is"** without any warranty of any kind. It is intended for educational, personal, or professional use in environments where validation and review are standard.

**Use in production systems is at your own risk.**

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**
