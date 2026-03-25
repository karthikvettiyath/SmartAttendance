import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import cv2
import numpy as np
from deepface import DeepFace
from mtcnn import MTCNN

STUDENT_NAMES = {
    1: "Karthik V R ",
    2: "Vivek Nair C",
    3: "Santhi Priyan",
    4: "Aditya",
    5: "Janita"
} 

def get_name(student_id: int) -> str:
    return STUDENT_NAMES.get(student_id, f"Unknown (ID: {student_id})")

# Helper to compute L2 distance (Euclidean)
def find_euclidean_distance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance

def run_recognition(model_path="trainer/encodings.pickle", confidence_threshold=10.0):
    """
    Opens webcam and runs real-time face recognition using DeepFace encodings.
    Threshold for Facenet Euclidean L2 is around 10.0 (DeepFace defaults).
    """
    try:
        with open(model_path, "rb") as f:
            data = pickle.loads(f.read())
    except FileNotFoundError:
        print(f"[ERROR] Could not load model from '{model_path}'.")
        return

    cap = cv2.VideoCapture(0)
    detector = MTCNN()

    print("[INFO] Real-time DeepFace Recognition started. Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb_frame)

        for face in faces:
            x, y, w, h = face['box']
            x, y = abs(x), abs(y)
            
            # Extract face crop
            face_crop = frame[y:y+h, x:x+w]
            if face_crop.size == 0: continue
            
            try:
                # Get embeddings for the detected face
                results = DeepFace.represent(face_crop, model_name="Facenet", enforce_detection=False)
                if len(results) > 0:
                    encoding = results[0]["embedding"]
                    
                    # Compare with all known encodings
                    best_match_id = "Unknown"
                    min_dist = float('inf')
                    
                    for i, known_encoding in enumerate(data["encodings"]):
                        dist = find_euclidean_distance(np.array(known_encoding), np.array(encoding))
                        if dist < min_dist:
                            min_dist = dist
                            best_match_id = data["names"][i]
                    
                    if min_dist < confidence_threshold:
                        color = (0, 255, 0)
                        label = f"{get_name(best_match_id)} [{min_dist:.2f}]"
                    else:
                        color = (0, 0, 255)
                        label = f"Unknown [{min_dist:.2f}]"
                        
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            except Exception as e:
                pass # Ignore DeepFace processing errors for invalid crops

        cv2.imshow("Smart Attendance – DL Recognition (ESC to quit)", frame)
        if cv2.waitKey(1) == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_recognition()
