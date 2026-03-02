import cv2
import os
import glob

def preprocess_images(student_dir):
    """
    Reads images from the student's directory, resizes them to 200x200,
    and applies simple normalization or checks if they are grayscale.
    """
    print(f"\n[INFO] Starting preprocessing for images in {student_dir}")
    
    image_paths = glob.glob(os.path.join(student_dir, "*.jpg"))
    if not image_paths:
        print("[WARNING] No images found to preprocess.")
        return False
        
    for img_path in image_paths:
        # Read image in grayscale explicitly
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            print(f"[WARNING] Could not read {img_path}. Skipping.")
            continue
            
        # Resize to 200x200
        resized = cv2.resize(img, (200, 200))
        
        # Overwrite the original
        cv2.imwrite(img_path, resized)
        
    print(f"[SUCCESS] Preprocessed {len(image_paths)} images successfully.")
    return True
