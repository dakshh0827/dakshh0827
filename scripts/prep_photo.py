import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path, output_path="source-prepped.png"):
    print(f"Loading: {input_path}")

    # Load original image
    img = Image.open(input_path).convert("RGBA")
    print(f"Image loaded: {img.size}")

    # 1. Remove background
    print("Removing background...")
    subject = remove(img)
    print("Background removed.")

    # Convert PIL image to numpy array
    rgba = np.array(subject)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # 2. Convert subject to grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Apply CLAHE for local contrast
    print("Applying CLAHE...")

    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # 3. Composite onto pure white background
    alpha_float = alpha.astype(np.float32) / 255.0

    result = (
        enhanced.astype(np.float32) * alpha_float
        + 255 * (1 - alpha_float)
    )

    result = np.clip(result, 0, 255).astype(np.uint8)

    # Save result
    Image.fromarray(result).save(output_path)

    print(f"Saved successfully: {output_path}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python scripts/prep_photo.py <image>")
        sys.exit(1)

    prep_photo(sys.argv[1])