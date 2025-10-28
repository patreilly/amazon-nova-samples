#!/usr/bin/env python3
import os
import sys
from pdf2image import convert_from_path
from pathlib import Path

def pdf_to_png(pdf_path, output_dir=None, dpi=200):
    # Validate input file
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        return
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.splitext(pdf_path)[0] + "_pages"
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Convert PDF to images
        print(f"Converting '{pdf_path}' to PNG images...")
        pages = convert_from_path(pdf_path, dpi=dpi)
        
        # Save each page as PNG
        for i, page in enumerate(pages, 1):
            output_path = os.path.join(output_dir, f"page_{i:03d}.png")
            page.save(output_path, 'PNG')
            print(f"Saved: {output_path}")
        
        print(f"\nConversion complete! {len(pages)} pages saved to '{output_dir}'")
        
    except Exception as e:
        print(f"Error converting PDF: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_png.py <pdf_file> [output_directory]")
        print("Example: python pdf_to_png.py document.pdf ./images")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    dpi = 200
    
    pdf_to_png(pdf_path, output_dir, dpi)

if __name__ == "__main__":
    main()