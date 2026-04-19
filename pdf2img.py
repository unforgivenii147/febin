#!/data/data/com.termux/files/usr/bin/python
import shutil
from pathlib import Path

from pdf2image import convert_from_path

# --- Configuration ---
# Path to Poppler's bin directory.
# If Poppler is in your system's PATH, you might be able to leave this as None.
# Example for Windows: r'C:\path\to\poppler-xx.xx.x\bin'
# Example for macOS (using Homebrew): '/usr/local/bin' or '/opt/homebrew/bin'
POPPLER_PATH = None


# --- Function to convert a single PDF ---
def convert_pdf_to_jpg(pdf_path: Path, output_folder: Path):
    try:
        print(f"Converting '{pdf_path.name}'...")
        # Create a subdirectory for the JPGs of this PDF
        pdf_output_dir = output_folder / pdf_path.stem
        pdf_output_dir.mkdir(parents=True, exist_ok=True)
        # Convert PDF pages to images
        images = convert_from_path(
            pdf_path=pdf_path,
            dpi=300,  # You can adjust DPI for quality (higher DPI = better quality, larger files)
            output_folder=pdf_output_dir,
            fmt="jpeg",
            thread_count=4,  # Use multiple threads for faster conversion
            poppler_path=POPPLER_PATH,
        )
        # Rename files to ensure sequential naming (e.g., mydoc_page_1.jpg)
        # and move them to the main output folder if desired, or keep in subdirs
        converted_files = []
        for i, _image_path in enumerate(images):
            # The 'images' variable contains PIL Image objects if output_folder is not specified
            # But convert_from_path with output_folder saves them directly.
            # We need to construct the expected filename based on Poppler's naming convention.
            # Poppler names files like: output_folder/pdf_filename-page_N.jpg
            expected_jpg_name = f"{pdf_path.stem}_page_{i + 1}.jpeg"
            source_jpg_path = pdf_output_dir / expected_jpg_name
            if source_jpg_path.exists():
                # Rename to .jpg extension
                final_jpg_path = pdf_output_dir / f"{pdf_path.stem}_page_{i + 1}.jpg"
                shutil.move(source_jpg_path, final_jpg_path)
                converted_files.append(final_jpg_path)
            else:
                print(f"Warning: Expected file {source_jpg_path} not found after conversion.")
        print(f"Successfully converted '{pdf_path.name}' to {len(converted_files)} JPG files in '{pdf_output_dir}'.")
        return True
    except Exception as e:
        print(f"Error converting '{pdf_path.name}': {e}")
        # Clean up potentially partially created directory if error occurred
        if "pdf_output_dir" in locals() and pdf_output_dir.exists():
            try:
                shutil.rmtree(pdf_output_dir)
            except Exception as cleanup_e:
                print(f"Error during cleanup of '{pdf_output_dir}': {cleanup_e}")
        return False


# --- Main script logic ---
def process_directory(start_dir: Path, output_base_dir: Path):
    print(f"Starting PDF to JPG conversion in directory: {start_dir}")
    print(f"Output will be saved in: {output_base_dir}")
    converted_count = 0
    failed_count = 0
    # Iterate through all files in the start directory recursively
    for item in start_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() == ".pdf":
            # Ensure we don't process PDFs already in the output directory if it's a subdirectory
            if output_base_dir in item.parents:
                print(f"Skipping PDF '{item.name}' as it's within the output directory.")
                continue
            if convert_pdf_to_jpg(item, output_base_dir):
                try:
                    # Remove the original PDF if conversion was successful
                    item.unlink()
                    print(f"Removed original PDF: '{item.name}'")
                    converted_count += 1
                except OSError as e:
                    print(f"Error removing original PDF '{item.name}': {e}")
                    failed_count += 1
            else:
                failed_count += 1
    print("\n--- Conversion Summary ---")
    print(f"Successfully converted and removed: {converted_count} PDF files.")
    print(f"Failed to convert: {failed_count} PDF files.")
    print("------------------------")


# --- Script Execution ---
if __name__ == "__main__":
    # --- Setup ---
    current_directory = Path.cwd()
    # Create an 'output_jpgs' directory in the current directory for the converted images
    output_directory = current_directory / "output_jpgs"
    output_directory.mkdir(exist_ok=True)
    # --- Run Conversion ---
    process_directory(current_directory, output_directory)
    print("\nScript finished.")
    print(f"Converted JPG files are located in: {output_directory}")
