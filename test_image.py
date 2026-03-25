import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import cv2
import numpy as np
from deepface import DeepFace
from mtcnn import MTCNN

IMAGE_PATH = r"d:\photos\Download\20250104_150152.jpg"
MODEL_PATH = "trainer/encodings.pickle"
OUTPUT_PATH = "output_test.jpg"

STUDENT_NAMES = {
    1: "Karthik V R ",
    2: "Vivek Nair C",
    3: "Santhi Priyan",
    4: "Aditya",
    5: "Janita"
} 

def get_name(student_id):
    return STUDENT_NAMES.get(student_id, f"Unknown (ID: {student_id})")

def find_euclidean_distance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance

def process_image():
    # Load encodings if available
    try:
        with open(MODEL_PATH, "rb") as f:
            data = pickle.loads(f.read())
            print("[INFO] Encodings loaded.")
    except Exception as e:
        print(f"[WARNING] Could not load encodings ({e}). All faces will be marked Unknown.")
        data = {"encodings": [], "names": []}

    frame = cv2.imread(IMAGE_PATH)
    if frame is None:
        print(f"[ERROR] Could not read image at {IMAGE_PATH}")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    detector = MTCNN()
    print("[INFO] Detecting faces using MTCNN, please wait...")
    faces = detector.detect_faces(rgb_frame)
    print(f"[INFO] Detected {len(faces)} faces.")

    for face in faces:
        x, y, w, h = face['box']
        x, y = abs(x), abs(y)
        face_crop = frame[y:y+h, x:x+w]
        
        if face_crop.size == 0: continue
            
        color = (0, 0, 255) # Default Red
        label = "Unknown"
        
        if len(data["encodings"]) > 0:
            try:
                results = DeepFace.represent(face_crop, model_name="Facenet", enforce_detection=False)
                if len(results) > 0:
                    encoding = results[0]["embedding"]
                    
                    best_match_id = "Unknown"
                    min_dist = float('inf')
                    
                    for i, known_encoding in enumerate(data["encodings"]):
                        dist = find_euclidean_distance(np.array(known_encoding), np.array(encoding))
                        if dist < min_dist:
                            min_dist = dist
                            best_match_id = data["names"][i]
                    
                    # 10.0 is the DeepFace default Euclidean threshold for Facenet
                    if min_dist < 10.0:
                        color = (0, 255, 0) # Green for match
                        label = f"{get_name(best_match_id)} [{min_dist:.2f}]"
                    else:
                        label = f"Unknown [{min_dist:.2f}]"
            except Exception as e:
                print(f"[ERROR] DeepFace embedding failed for crop: {e}")
                
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Draw background pill for text readablility
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_y = y - 10 if y - 10 > 10 else y + h + 20
        (tw, th), _ = cv2.getTextSize(label, font, 0.9, 3)
        cv2.rectangle(frame, (x, text_y - th - 5), (x + tw + 5, text_y + 5), color, -1)
        cv2.putText(frame, label, (x + 2, text_y), font, 0.9, (0, 0, 0), 3)
        
    cv2.imwrite(OUTPUT_PATH, frame)
    print(f"[SUCCESS] Processed image and saved result to {OUTPUT_PATH}")

if __name__ == "__main__":
    process_image()
