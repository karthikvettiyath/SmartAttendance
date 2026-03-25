import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import cv2
import pickle
from deepface import DeepFace

def train_model(dataset_dir="dataset", model_output_path="trainer/encodings.pickle"):
    """
    Extracts face encodings using DeepFace (Facenet model - 128D) and saves them as a pickle.
    """
    print("========================================")
    print("       DeepFace Embeddings Training     ")
    print("========================================\n")

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    
    known_encodings = []
    known_ids = []

    if not os.path.exists(dataset_dir):
        print(f"[ERROR] Dataset directory '{dataset_dir}' not found.")
        return False

    student_folders = [f for f in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, f))]
    if not student_folders: return False

    for student_id_str in student_folders:
        try: student_id = int(student_id_str)
        except ValueError: continue
            
        student_path = os.path.join(dataset_dir, student_id_str)
        print(f"[INFO] Processing images for Student ID: {student_id}")
        
        for img_file in os.listdir(student_path):
            img_path = os.path.join(student_path, img_file)
            
            try:
                # DeepFace represent extracts the embedding automatically.
                # enforce_detection=False just in case the crop bounding box isn't perfect for DeepFace's internal detector target.
                results = DeepFace.represent(img_path, model_name="Facenet", enforce_detection=False)
                # results is a list of dicts (if multiple faces). We assume 1 face per crop.
                if len(results) > 0:
                    encoding = results[0]["embedding"]
                    known_encodings.append(encoding)
                    known_ids.append(student_id)
            except Exception as e:
                print(f"[WARNING] Skipping {img_file}: {e}")
                
    print(f"\n[INFO] Successfully processed {len(known_encodings)} face encodings.")
    
    data = {"encodings": known_encodings, "names": known_ids}
    with open(model_output_path, "wb") as f:
        f.write(pickle.dumps(data))
        
    print(f"[SUCCESS] Encodings saved to: {model_output_path}")
    print("========================================")
    return True

if __name__ == "__main__":
    train_model()
