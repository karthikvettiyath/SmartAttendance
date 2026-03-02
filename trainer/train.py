import cv2
import os
import numpy as np

def get_images_and_labels(dataset_dir):
    """
    Walks through the dataset directory and returns:
    - List of face images (grayscale numpy arrays)
    - List of corresponding integer student IDs (labels)
    """
    face_samples = []
    ids = []

    if not os.path.exists(dataset_dir):
        print(f"[ERROR] Dataset directory '{dataset_dir}' not found.")
        return face_samples, ids

    student_folders = [f for f in os.listdir(dataset_dir)
                       if os.path.isdir(os.path.join(dataset_dir, f))]

    if not student_folders:
        print("[ERROR] No student folders found in dataset.")
        return face_samples, ids

    for student_id_str in student_folders:
        try:
            student_id = int(student_id_str)
        except ValueError:
            print(f"[WARNING] Skipping folder '{student_id_str}' – not a valid numeric ID.")
            continue

        student_path = os.path.join(dataset_dir, student_id_str)

        for img_file in os.listdir(student_path):
            img_path = os.path.join(student_path, img_file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                print(f"[WARNING] Could not read {img_path}. Skipping.")
                continue

            face_samples.append(img)
            ids.append(student_id)

    return face_samples, ids


def train_model(dataset_dir="dataset", model_output_path="trainer/model.yml"):
    """
    Trains an LBPH face recognizer on the dataset and saves the model.
    """
    print("========================================")
    print("       LBPH Face Recognizer Training    ")
    print("========================================\n")

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)

    print("[INFO] Reading images from dataset...")
    faces, ids = get_images_and_labels(dataset_dir)

    if not faces:
        print("[ERROR] No training data found. Run dataset capture first.")
        return False

    print(f"[INFO] Found {len(faces)} images across {len(set(ids))} student(s).")
    print("[INFO] Training LBPH model... (this may take a moment)")

    # Initialize and train the LBPH recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))

    # Save the trained model
    recognizer.save(model_output_path)

    print(f"\n[SUCCESS] Model trained and saved to: {model_output_path}")
    print("========================================")
    return True


if __name__ == "__main__":
    train_model()
