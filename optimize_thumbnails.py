#!/usr/bin/env python3
"""Optimize all thumbnail images in the thumbnails directory"""
import os
from PIL import Image
from pathlib import Path


def is_already_optimized(filepath):
    """Check if image is already optimized (JPEG, width <= 300px)"""
    try:
        with Image.open(filepath) as img:
            # Check if it's JPEG and already at target size
            if img.format == 'JPEG' and img.width <= 300:
                return True
        return False
    except Exception:
        return False


def optimize_image(filepath):
    """Resize and optimize a single image file"""
    try:
        # Create backup path
        temp_path = str(filepath) + '.temp'
        backup_path = str(filepath) + '.backup'
        
        # Open image
        img = Image.open(filepath)
        
        # Skip if already optimized
        if img.format == 'JPEG' and img.width <= 300:
            print(f"  ✓ Already optimized: {filepath.name}")
            return True
        
        print(f"  Processing: {filepath.name} ({img.width}x{img.height}, {img.mode})")
        
        # Convert RGBA or P mode images to RGB for JPEG
        if img.mode in ('RGBA', 'P', 'LA'):
            # Create white background
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to max width of 300px while maintaining aspect ratio
        max_width = 300
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Backup original if format is changing
        if not str(filepath).endswith('.jpg') and not str(filepath).endswith('.jpeg'):
            os.rename(filepath, backup_path)
            new_filepath = filepath.with_suffix('.jpg')
        else:
            new_filepath = filepath
        
        # Save with optimization and reduced quality
        img.save(new_filepath, 'JPEG', quality=85, optimize=True)
        
        # Remove backup if successful
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
        
        print(f"    ✓ Optimized: {new_filepath.name} ({img.width}x{img.height})")
        return True
        
    except Exception as e:
        print(f"    ✗ Error processing {filepath.name}: {e}")
        # Restore backup if it exists
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, filepath)
        return False


def main():
    """Process all images in thumbnails directory"""
    thumbnails_dir = Path(__file__).parent / 'thumbnails'
    
    if not thumbnails_dir.exists():
        print(f"Error: Directory not found: {thumbnails_dir}")
        return
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_files = [
        f for f in thumbnails_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"No image files found in {thumbnails_dir}")
        return
    
    print(f"Found {len(image_files)} image files in {thumbnails_dir}")
    print()
    
    processed = 0
    skipped = 0
    errors = 0
    
    for image_file in sorted(image_files):
        if is_already_optimized(image_file):
            skipped += 1
        elif optimize_image(image_file):
            processed += 1
        else:
            errors += 1
    
    print()
    print(f"Summary:")
    print(f"  Processed: {processed}")
    print(f"  Skipped (already optimized): {skipped}")
    print(f"  Errors: {errors}")


if __name__ == '__main__':
    main()
