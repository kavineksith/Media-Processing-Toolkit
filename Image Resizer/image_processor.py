import os
import sys
from PIL import Image
from pathlib import Path
from datetime import datetime
import concurrent.futures
import logging
from tqdm import tqdm

class ImageProcessor:
    def __init__(self, input_dir, output_dir, target_size=(1920, 1080)):
        """
        Initialize the ImageProcessor with directories and target size.
        
        Args:
            input_dir (str): Path to input directory with images
            output_dir (str): Path to output directory
            target_size (tuple): Target resolution (width, height)
        """
        self.input_dir = Path(input_dir).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.target_size = target_size
        
        # Initialize the logger
        self.logger = logging.getLogger(__name__)
        
        # Then validate directories
        self.validate_directories()
        
        # After directories are valid, configure full logging with file
        self.setup_file_logging()
        
    def setup_file_logging(self):
        """Configure full logging with file output after directories are validated."""
        
        # Configuration of the file handler
        loggin_handler = logging.FileHandler(self.output_dir / 'image_processor.log')
        loggin_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        self.logger.addHandler(loggin_handler)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"ImageProcessor initialized. Target size: {self.target_size}")
        
    def validate_directories(self):
        """Validate input and output directories."""
        # Check input directory
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")
            
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory ready: {self.output_dir}")
        
    def get_supported_extensions(self):
        """Return supported image file extensions."""
        return ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
        
    def find_image_files(self):
        """Find all image files in the input directory."""
        image_files = []
        processed_paths = set()  # Track processed file paths to avoid duplicates
        
        for ext in self.get_supported_extensions():
            # Find files with lowercase extensions
            for file_path in self.input_dir.glob(f'*{ext}'):
                # Use Path.resolve() to get canonical path
                canonical_path = file_path.resolve()
                canonical_path_str = str(canonical_path).lower()
                
                if canonical_path_str not in processed_paths:
                    processed_paths.add(canonical_path_str)
                    image_files.append(canonical_path)
            
            # Find files with uppercase extensions
            for file_path in self.input_dir.glob(f'*{ext.upper()}'):
                canonical_path = file_path.resolve()
                canonical_path_str = str(canonical_path).lower()
                
                if canonical_path_str not in processed_paths:
                    processed_paths.add(canonical_path_str)
                    image_files.append(canonical_path)
        
        self.logger.info(f"Found {len(image_files)} unique image files")
        return sorted(image_files)  # Sort files for consistent ordering
        
    def generate_output_filename(self, index, original_path):
        """
        Generate output filename in format 'wallpaper - 001'.
        
        Args:
            index (int): Sequential number for the file
            original_path (Path): Original file path for extension
            
        Returns:
            Path: Output file path
        """
        ext = original_path.suffix.lower()
        return self.output_dir / f"wallpaper - {index:03d}{ext}"
        
    def process_single_image(self, image_path, output_path):
        """
        Process a single image file.
        
        Args:
            image_path (Path): Path to input image
            output_path (Path): Path to save processed image
            
        Returns:
            tuple: (success (bool), message (str))
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed (for PNG with alpha channel)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                target_width, target_height = self.target_size
                
                # Calculate the original aspect ratio
                original_aspect = original_width / original_height
                target_aspect = target_width / target_height
                
                if original_aspect == target_aspect:
                    # Perfect aspect ratio match - just resize to target
                    processed_img = img.resize(self.target_size, Image.LANCZOS)
                    fit_method = "exact resize"
                elif original_aspect > target_aspect:
                    # Image is wider than target aspect - fit to width
                    new_height = int(target_width / original_aspect)
                    processed_img = img.resize((target_width, new_height), Image.LANCZOS)
                    fit_method = "width-constrained resize"
                else:
                    # Image is taller than target aspect - fit to height
                    new_width = int(target_height * original_aspect)
                    processed_img = img.resize((new_width, target_height), Image.LANCZOS)
                    fit_method = "height-constrained resize"
                
                # Save with maximum quality
                if output_path.suffix.lower() in ('.jpg', '.jpeg'):
                    processed_img.save(output_path, quality=95, optimize=True, subsampling=0)
                else:
                    processed_img.save(output_path, optimize=True)
                    
            return True, f"Successfully processed {image_path.name} ({fit_method})"
            
        except Exception as e:
            return False, f"Failed to process {image_path.name}: {str(e)}"
            
    def process_images(self, max_workers=None):
        """
        Process all images in the input directory.
        
        Args:
            max_workers (int): Number of worker threads for parallel processing
            
        Returns:
            dict: Processing statistics
        """
        image_files = self.find_image_files()
        if not image_files:
            self.logger.warning("No image files found in input directory")
            return {'total': 0, 'success': 0, 'failed': 0}
            
        # Remove duplicates by converting to set of file paths (case-insensitive)
        image_files_set = set()
        unique_image_files = []
        for img_path in image_files:
            # Use lowercase path string as key to detect case-insensitive duplicates
            path_key = str(img_path).lower()
            if path_key not in image_files_set:
                image_files_set.add(path_key)
                unique_image_files.append(img_path)
                
        self.logger.info(f"Found {len(image_files)} total images, {len(unique_image_files)} unique images after deduplication")
        image_files = unique_image_files
            
        stats = {'total': len(image_files), 'success': 0, 'failed': 0}
        self.logger.info(f"Processing {stats['total']} unique images")
        
        # Create a lock for thread-safe progress bar updates
        progress_lock = threading.Lock()
        
        # Create a simple static progress bar
        with tqdm(total=stats['total'], desc="Processing images", unit="img") as pbar:
            # Track processed files to prevent duplicates in output
            processed_files = set()
            
            if max_workers and max_workers > 1:
                # Parallel processing
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    for idx, img_path in enumerate(image_files, 1):
                        output_path = self.generate_output_filename(idx, img_path)
                        futures.append(executor.submit(
                            self.process_single_image, img_path, output_path
                        ))
                        
                    for future in concurrent.futures.as_completed(futures):
                        success, message = future.result()
                        with progress_lock:
                            if success:
                                stats['success'] += 1
                                self.logger.info(message)
                            else:
                                stats['failed'] += 1
                                self.logger.error(message)
                            # Simple progress update
                            pbar.update(1)
            else:
                # Sequential processing
                for idx, img_path in enumerate(image_files, 1):
                    # Skip if we've already processed this file (based on name)
                    file_key = img_path.name.lower()
                    if file_key in processed_files:
                        self.logger.warning(f"Skipping duplicate file: {img_path.name}")
                        continue
                        
                    processed_files.add(file_key)
                    output_path = self.generate_output_filename(idx, img_path)
                    success, message = self.process_single_image(img_path, output_path)
                    if success:
                        stats['success'] += 1
                        self.logger.info(message)
                    else:
                        stats['failed'] += 1
                        self.logger.error(message)
                    # Simple progress update
                    pbar.update(1)
                    
        self.logger.info(
            f"Processing complete. Success: {stats['success']}, Failed: {stats['failed']}"
        )
        return stats
        
def main():
    """Main execution function."""
    try:
        # Configuration
        input_directory = input("Enter input directory path: ").strip()
        output_directory = input("Enter output directory path (default: 'output'): ").strip() or "output"
        target_resolution = (1920, 1080)
        
        # Add timestamp to output directory to prevent overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_output_directory = f"{output_directory}_{timestamp}"
        
        print(f"Initializing image processor...")
        # Initialize processor with the timestamped directory
        processor = ImageProcessor(input_directory, timestamped_output_directory, target_resolution)
        
        # Detect CPU cores and set thread count
        max_workers = min(4, os.cpu_count() or 4)
        print(f"Processing images using {max_workers} worker threads")
        
        # Process images with a simple static progress bar
        stats = processor.process_images(max_workers=max_workers)
        
        print(f"\nProcessing Summary:")
        print(f"Total images: {stats['total']}")
        print(f"Successfully processed: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"Output directory: {timestamped_output_directory}")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    import threading  # Add import at the top of the file
    main()
    sys.exit(0)
