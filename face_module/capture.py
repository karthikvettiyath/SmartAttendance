import cv2
import os

def capture_student_faces(student_id, target_dir, num_images=50):
    """
    Captures faces from the webcam and saves them as grayscale images.
    """
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    if face_cascade.empty():
        print("[ERROR] Failed to load haarcascade_frontalface_default.xml")
        return False
        
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return False
        
    print("[INFO] Starting face capture. Please look at the camera.")
    print(f"[INFO] Waiting for {num_images} images to be captured...")
    
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Increment capture count
            count += 1
            
            # Save the captured face image
            face_img = gray[y:y + h, x:x + w]
            img_path = os.path.join(target_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face_img)
            
            # Briefly pause face detection for visual feedback
            cv2.waitKey(100)
            
            if count >= num_images:
                break
                
        cv2.imshow("Face Capture", frame)
        
        # Press 'ESC' to exit early or automatically stop after num_images
        if cv2.waitKey(1) == 27 or count >= num_images:
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
    if count >= num_images:
        print(f"\n[SUCCESS] Successfully captured {num_images} faces for student ID {student_id}")
        return True
    else:
        print(f"\n[WARNING] Captured {count}/{num_images} faces.")
        return False
