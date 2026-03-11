import cv2
import os
import numpy as np

def preprocess_image(image_bytes):
    # 1. Load Image from bytes into numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Provided bytes could not be decoded into an image.")
    
    # 2. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Remove Noise (Light Blur)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. ADAPTIVE THRESHOLDING
    thresh = cv2.adaptiveThreshold(
        blur, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )

    # 5. Dilation/Erosion (Optional Cleanup)
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.erode(thresh, kernel, iterations=1) 

    return processed

if __name__ == "__main__":
    # Test run
    try:
        preprocess_image("images/input.jpg", "output/processed.png", show_preview=True)
    except Exception as e:
        print(f"Error: {e}")