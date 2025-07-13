import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import argparse
from pathlib import Path
from PIL import Image

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

def main(args):
    # Create the options for the segmenter
    base_options = python.BaseOptions(model_asset_path=args.model)
    options = vision.ImageSegmenterOptions(base_options=base_options,
                                           output_category_mask=True,
                                           output_confidence_masks=True)

    # Create the segmenter
    with vision.ImageSegmenter.create_from_options(options) as segmenter:
        # Read the image (supports HEIC, PNG, JPEG)
        try:
            image = load_image(args.image)
        except Exception as e:
            raise ValueError(f"Failed to read image from {args.image}: {e}")

        # Convert to RGB (MediaPipe uses RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        # Perform segmentation
        segmentation_result = segmenter.segment(mp_image)

        # Get the category mask
        category_mask = segmentation_result.category_mask.numpy_view()

        # Define class names
        class_names = ['background', 'hair', 'body-skin', 'face-skin', 'clothes', 'accessories']

        # Create output directory if it doesn't exist
        output_dir = args.output_dir if args.output_dir else args.output
        os.makedirs(output_dir, exist_ok=True)

        # Create and save binary masks for each class
        for class_id, class_name in enumerate(class_names):
            binary_mask = (category_mask == class_id).astype(np.uint8) * 255
            output_path = os.path.join(output_dir, f'{class_name}_mask.png')
            cv2.imwrite(output_path, binary_mask)
            print(f"Saved mask for {class_name} to {output_path}")

        # Optionally, create a colored visualization of the segmentation
        colored_mask = np.zeros((category_mask.shape[0], category_mask.shape[1], 3), dtype=np.uint8)
        colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        for class_id, color in enumerate(colors):
            colored_mask[category_mask == class_id] = color

        cv2.imwrite(os.path.join(output_dir, 'colored_segmentation.png'), colored_mask)
        print(f"Saved colored segmentation visualization to {os.path.join(output_dir, 'colored_segmentation.png')}")

    print("Segmentation complete. Check the output files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-class Selfie Segmentation")
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--model", default="selfie_multiclass_256x256.tflite", help="Path to the TFLite model")
    parser.add_argument("--output", default="output", help="Directory to save output masks (for backwards compatibility)")
    parser.add_argument("--output_dir", help="New argument: Directory to save output masks")
    args = parser.parse_args()

    main(args)