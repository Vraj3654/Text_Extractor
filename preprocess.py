import cv2
import os
import numpy as np

def preprocess_image(input_path, output_path, show_preview=False):
    # 1. Validation
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Load Image
    img = cv2.imread(input_path)
    
    # 3. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 4. Remove Noise (Light Blur)
    # This removes the "grain" from the paper texture
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 5. ADAPTIVE THRESHOLDING (The "Scanner" Fix)
    # Instead of one global value, this calculates local thresholds.
    # Block Size (11) and C (2) are tunable, but 11/2 is standard for docs.
    thresh = cv2.adaptiveThreshold(
        blur, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )

    # 6. Dilation/Erosion (Optional Cleanup)
    # This connects broken letters which is common in adaptive thresholding
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.erode(thresh, kernel, iterations=1) 

    # 7. Save
    cv2.imwrite(output_path, processed)
    print(f"✅ Preprocessing complete. Saved to: {output_path}")

    # Preview
    if show_preview:
        # Resize for screen if massive
        h, w = processed.shape
        if h > 800:
            scale = 800 / h
            dim = (int(w * scale), 800)
            preview = cv2.resize(processed, dim)
        else:
            preview = processed
            
        cv2.imshow("Scanner Mode Preview", preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return output_path

if __name__ == "__main__":
    # Test run
    try:
        preprocess_image("images/input.jpg", "output/processed.png", show_preview=True)
    except Exception as e:
        print(f"Error: {e}")