
"""
retinex_flatten.py v2
--------------------
Luminance-only Retinex with optional skin masking for baked textures & source photos.

Key improvements:
- Operates on Y channel only (YUV) to avoid chroma halos
- Optional MediaPipe skin masking to preserve non-skin areas
- Higher default sigma for better results on 4K textures

Usage examples
--------------

# Single baked texture with skin masking
python retinex_flatten.py /path/to/baked_mesh_tex0.png --sigma 140 --mask-skin

# All images in a folder with gentle blending
python retinex_flatten.py /path/to/scan_001/images --sigma 140 --blend 0.3
"""

import cv2
import os
import sys
import numpy as np
from pathlib import Path
from typing import List, Optional
from PIL import Image

def load_image(path: Path) -> np.ndarray:
    """Return BGR uint8 image for PNG/JPEG/HEIC."""
    ext = path.suffix.lower()
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
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def build_skin_mask(scan_root: Path, img_shape: tuple) -> Optional[np.ndarray]:
    """Build skin mask using MediaPipe on source photos."""
    try:
        import mediapipe as mp
    except ImportError:
        print("MediaPipe not available. Install with: pip install mediapipe")
        return None
    
    cache_path = scan_root / "skin_mask.png"
    if cache_path.exists():
        print(f"Loading cached skin mask: {cache_path}")
        mask = cv2.imread(str(cache_path), cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            return cv2.resize(mask, (img_shape[1], img_shape[0])) / 255.0
    
    print("Building skin mask with MediaPipe...")
    
    # Initialize MediaPipe
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    
    # Find source photos
    photo_exts = ['.jpg', '.jpeg', '.png', '.heic']
    photos = []
    for ext in photo_exts:
        photos.extend(scan_root.rglob(f'*{ext}'))
        photos.extend(scan_root.rglob(f'*{ext.upper()}'))
    
    if not photos:
        print("No source photos found for mask generation")
        return None
    
    # Process a subset of photos to build mask
    mask_accum = np.zeros(img_shape[:2], dtype=np.float32)
    processed = 0
    
    for photo_path in photos[:20]:  # Limit to first 20 photos
        try:
            photo = load_image(photo_path)
            photo_rgb = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
            
            # Run segmentation
            results = selfie_segmentation.process(photo_rgb)
            if results.segmentation_mask is not None:
                # Resize mask to target shape and accumulate
                mask_resized = cv2.resize(results.segmentation_mask, (img_shape[1], img_shape[0]))
                mask_accum += mask_resized
                processed += 1
                
        except Exception as e:
            print(f"Skipping {photo_path}: {e}")
            continue
    
    selfie_segmentation.close()
    
    if processed == 0:
        return None
    
    # Normalize and threshold
    mask_final = mask_accum / processed
    mask_final = (mask_final > 0.5).astype(np.uint8) * 255
    
    # Cache the mask
    cv2.imwrite(str(cache_path), mask_final)
    print(f"Cached skin mask: {cache_path}")
    
    return mask_final.astype(np.float32) / 255.0

def retinex_luminance(img: np.ndarray, sigma: float = 140.0, skin_mask: Optional[np.ndarray] = None, blend: float = 1.0) -> np.ndarray:
    """Luminance-only Retinex with optional skin masking."""
    
    # Convert to YUV and work on Y channel only
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV).astype(np.float32)
    Y_orig = yuv[..., 0] / 255.0
    Y = Y_orig + 1e-6
    
    # Apply Retinex on luminance
    log_Y = np.log(Y)
    blur = cv2.GaussianBlur(log_Y, (0, 0), sigmaX=sigma, sigmaY=sigma)
    flat_Y = np.exp(log_Y - blur)
    flat_Y = np.clip(flat_Y, 0.0, 1.0)
    
    # Apply skin mask if provided
    if skin_mask is not None:
        flat_Y = np.where(skin_mask > 0.5, flat_Y, Y_orig)
    
    # Blend original and flattened
    if blend < 1.0:
        flat_Y = blend * flat_Y + (1.0 - blend) * Y_orig
    
    # Put Y back, leave U/V untouched
    yuv[..., 0] = np.clip(flat_Y * 255, 0, 255)
    result = cv2.cvtColor(yuv.astype(np.uint8), cv2.COLOR_YUV2BGR)
    
    return result

def gather_files(root: Path, exts: List[str]) -> List[Path]:
    if root.is_file():
        return [root]
    matches = []
    for p in root.rglob('*'):
        if p.suffix.lower() in exts:
            matches.append(p)
    return matches

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path, help='file or directory')
    parser.add_argument('--sigma', type=float, default=140.0,
                        help='Gaussian σ in pixels (default: 140 for 4K textures)')
    parser.add_argument('--mask-skin', action='store_true',
                        help='Use MediaPipe to mask non-skin areas')
    parser.add_argument('--blend', type=float, default=1.0,
                        help='Blend factor: 1.0=full flatten, 0.3=gentle (default: 1.0)')
    args = parser.parse_args()

    files = gather_files(args.input, exts=['.png', '.jpg', '.jpeg', '.heic'])
    if not files:
        print('No images found.', file=sys.stderr)
        sys.exit(1)

    out_dir = (args.input.parent if args.input.is_file() else args.input) / 'flattened'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build skin mask once if requested
    skin_mask = None
    if args.mask_skin:
        # Use first image to determine shape, assume scan root is input directory
        first_img = load_image(files[0])
        scan_root = args.input if args.input.is_dir() else args.input.parent
        skin_mask = build_skin_mask(scan_root, first_img.shape)
        if skin_mask is None:
            print("Warning: Could not build skin mask, proceeding without masking")

    for f in files:
        img = load_image(f)
        
        # Resize skin mask if needed
        current_mask = skin_mask
        if skin_mask is not None and skin_mask.shape[:2] != img.shape[:2]:
            current_mask = cv2.resize(skin_mask, (img.shape[1], img.shape[0]))
        
        flat = retinex_luminance(img, sigma=args.sigma, skin_mask=current_mask, blend=args.blend)
        
        # Create output filename
        out_name = f.stem + '_flat' + f.suffix
        if f.suffix.lower() != '.png':
            out_name = f.stem + '_flat.png'
        out_path = out_dir / out_name
        
        cv2.imwrite(str(out_path), flat)
        print('✔', out_path)

if __name__ == '__main__':
    main()
