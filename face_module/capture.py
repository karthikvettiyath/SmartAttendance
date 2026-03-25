import cv2
import os
from mtcnn import MTCNN

def capture_student_faces(student_id, target_dir, num_images=50):
    """
    Captures faces from the webcam using MTCNN and saves them as images.
    Includes guided instructions for different face angles.
    """
    detector = MTCNN()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return False
        
    print("[INFO] Starting guided face capture.")
    print(f"[INFO] Waiting for {num_images} images to be captured...")
    
    count = 0
    instructions = [
        (0, 10, "Look Straight"),
        (10, 20, "Turn Right Slightly"),
        (20, 30, "Turn Left Slightly"),
        (30, 40, "Tilt Up Slightly"),
        (40, 50, "Tilt Down Slightly")
    ]
    
    current_instruction = instructions[0][2]
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break
            
        # MTCNN uses RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.detect_faces(rgb_frame)
        
        # Determine current instruction
        for start, end, instr in instructions:
            if start <= count < end:
                current_instruction = instr
                break
                
        # Draw instruction UI
        cv2.putText(frame, f"Task: {current_instruction} ({count}/{num_images})", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    
        if results:
            # Pick the largest face in the frame
            largest_face = max(results, key=lambda b: b['box'][2] * b['box'][3])
            x, y, w, h = largest_face['box']
            x, y = abs(x), abs(y)
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Save the captured face crop
            face_img = frame[y:y + h, x:x + w]
            if face_img.size > 0:
                count += 1
                img_path = os.path.join(target_dir, f"{count}.jpg")
                cv2.imwrite(img_path, face_img)
                cv2.waitKey(200) # Ensure a slight delay so images are diverse
            
        cv2.imshow("Guided Face Capture", frame)
        
        # Press ESC or hit max images to stop
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
