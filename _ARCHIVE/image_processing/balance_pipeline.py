#!/usr/bin/env python3
"""
balance_pipeline.py
------------------
Pre-photogrammetry image processing pipeline:
1. Remove background (replace with black)
2. Balance overall luminance to hero image
3. Extra pass on skin luminance
4. Save intermediate results for verification

Usage:
python balance_pipeline.py --input_dir /path/to/scan/images --hero_image front.heic
"""

import cv2
import numpy as np
import argparse
from pathlib import Path
from PIL import Image
import os
import shutil
import subprocess
import sys

# Import the load_image function we'll reuse
def load_image(path: str) -> np.ndarray:
    """Load image supporting HEIC, PNG, JPEG formats. Returns BGR numpy array."""
    path_obj = Path(path)
    ext = path_obj.suffix.lower()
    
    if ext == '.heic':
        try:
            import pillow_heif
            heif = pillow_heif.read_heif(path)
            img = Image.frombytes(
                heif.mode, heif.size, heif.data,
                "raw", heif.mode, heif.stride
            )
        except ImportError as e:
            raise RuntimeError(
                'pip install pillow-heif to open HEIC files'
            ) from e
    else:
        img = Image.open(path)
    
    # Convert PIL to BGR numpy array (OpenCV format)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def generate_masks(image_path, model_path="selfie_multiclass_256x256.tflite"):
    """Generate segmentation masks for a single image."""
    # Run mask_generator.py and capture the output directory
    output_dir = Path(image_path).stem + "_masks"
    cmd = [
        sys.executable,
        "mask_generator.py",
        "--image", str(image_path),
        "--model", model_path,
        "--output_dir", str(output_dir)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Mask generation failed: {result.stderr}")
    
    # Load the masks we need
    masks = {
        'background': cv2.imread(f"{output_dir}/background_mask.png", cv2.IMREAD_GRAYSCALE),
        'face-skin': cv2.imread(f"{output_dir}/face-skin_mask.png", cv2.IMREAD_GRAYSCALE),
        'body-skin': cv2.imread(f"{output_dir}/body-skin_mask.png", cv2.IMREAD_GRAYSCALE)
    }
    
    # Clean up temporary mask directory
    shutil.rmtree(output_dir)
    
    return masks


def remove_background(image, background_mask, bg_color=(0, 0, 0)):
    """Replace background with solid color (default black)."""
    # Invert mask (we want to keep non-background)
    subject_mask = cv2.bitwise_not(background_mask)
    
    # Create result image
    result = np.full_like(image, bg_color, dtype=np.uint8)
    
    # Copy subject pixels
    for c in range(3):
        result[:, :, c] = np.where(subject_mask > 0, image[:, :, c], bg_color[c])
    
    return result


def calculate_luminance_stats(image, mask=None):
    """Calculate mean luminance in YUV space, optionally within mask."""
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    y_channel = yuv[:, :, 0]
    
    if mask is not None:
        # Only consider pixels where mask > 0
        masked_pixels = y_channel[mask > 0]
        if len(masked_pixels) == 0:
            return None
        return np.mean(masked_pixels)
    else:
        return np.mean(y_channel)


def balance_luminance(image, target_luminance, current_luminance=None, mask=None):
    """Adjust image luminance to match target, optionally within mask."""
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV).astype(np.float32)
    
    # Calculate current luminance if not provided
    if current_luminance is None:
        current_luminance = calculate_luminance_stats(image, mask)
    
    if current_luminance is None or current_luminance == 0:
        return image
    
    # Calculate adjustment factor
    factor = target_luminance / current_luminance
    
    # Apply adjustment to Y channel
    if mask is not None:
        # Only adjust within mask
        yuv[:, :, 0] = np.where(mask > 0, 
                                yuv[:, :, 0] * factor, 
                                yuv[:, :, 0])
    else:
        yuv[:, :, 0] *= factor
    
    # Clip values and convert back
    yuv[:, :, 0] = np.clip(yuv[:, :, 0], 0, 255)
    result = cv2.cvtColor(yuv.astype(np.uint8), cv2.COLOR_YUV2BGR)
    
    return result


def process_scan(input_dir, hero_image_name, output_base_dir=None):
    """Process all images in a scan directory."""
    input_path = Path(input_dir)
    
    # Setup output directories
    if output_base_dir is None:
        output_base_dir = input_path.parent / f"{input_path.name}_processed"
    else:
        output_base_dir = Path(output_base_dir)
    
    # Create subdirectories for each step
    dirs = {
        'step1_masked': output_base_dir / '01_background_removed',
        'step2_balanced': output_base_dir / '02_luminance_balanced',
        'step3_skin': output_base_dir / '03_skin_balanced'
    }
    
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    
    # Find all images
    image_extensions = ['.heic', '.jpg', '.jpeg', '.png']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        raise ValueError(f"No images found in {input_dir}")
    
    print(f"Found {len(image_files)} images to process")
    
    # Find hero image
    hero_path = None
    for img in image_files:
        if hero_image_name.lower() in img.name.lower():
            hero_path = img
            break
    
    if hero_path is None:
        raise ValueError(f"Hero image '{hero_image_name}' not found")
    
    print(f"Using hero image: {hero_path.name}")
    
    # Process hero image first to get reference luminance values
    print("\nProcessing hero image...")
    hero_img = load_image(str(hero_path))
    hero_masks = generate_masks(hero_path)
    
    # Create combined skin mask
    hero_skin_mask = cv2.bitwise_or(hero_masks['face-skin'], hero_masks['body-skin'])
    
    # Calculate reference luminance values
    hero_overall_lum = calculate_luminance_stats(hero_img)
    hero_skin_lum = calculate_luminance_stats(hero_img, hero_skin_mask)
    
    print(f"Hero image luminance - Overall: {hero_overall_lum:.1f}, Skin: {hero_skin_lum:.1f}")
    
    # Process all images
    for i, img_path in enumerate(image_files, 1):
        print(f"\nProcessing {i}/{len(image_files)}: {img_path.name}")
        
        # Load image
        img = load_image(str(img_path))
        
        # Generate masks
        print("  - Generating masks...")
        masks = generate_masks(img_path)
        
        # Step 1: Remove background
        print("  - Removing background...")
        img_masked = remove_background(img, masks['background'])
        output_name = img_path.stem + '.png'  # Convert to PNG for output
        cv2.imwrite(str(dirs['step1_masked'] / output_name), img_masked)
        
        # Step 2: Balance overall luminance (excluding background)
        print("  - Balancing overall luminance...")
        # Create subject mask (inverse of background)
        subject_mask = cv2.bitwise_not(masks['background'])
        img_balanced = balance_luminance(img_masked, hero_overall_lum, mask=subject_mask)
        cv2.imwrite(str(dirs['step2_balanced'] / output_name), img_balanced)
        
        # Step 3: Extra pass on skin
        print("  - Balancing skin luminance...")
        # Combine face and body skin masks
        skin_mask = cv2.bitwise_or(masks['face-skin'], masks['body-skin'])
        img_skin_balanced = balance_luminance(img_balanced, hero_skin_lum, mask=skin_mask)
        cv2.imwrite(str(dirs['step3_skin'] / output_name), img_skin_balanced)
    
    print(f"\nProcessing complete! Results saved to: {output_base_dir}")
    return output_base_dir


def main():
    parser = argparse.ArgumentParser(description="Pre-photogrammetry image balancing pipeline")
    parser.add_argument("--input_dir", required=True, help="Directory containing source images")
    parser.add_argument("--hero_image", required=True, help="Name (or partial name) of hero/reference image")
    parser.add_argument("--output_dir", help="Output directory (default: input_dir_processed)")
    args = parser.parse_args()
    
    try:
        output_dir = process_scan(args.input_dir, args.hero_image, args.output_dir)
        print(f"\nSuccess! Check the results in:\n{output_dir}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 