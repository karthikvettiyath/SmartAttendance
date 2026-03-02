import cv2

# A simple name map: student_id (int) → name (str)
# Add more students here as you enroll them
STUDENT_NAMES = {
    1: "Karthik V R ",
    2: "Vivek Nair C",
    3: "Santhipriyan",
}

def get_name(student_id: int) -> str:
    return STUDENT_NAMES.get(student_id, f"Unknown (ID: {student_id})")


def run_recognition(model_path="trainer/model.yml",
                    cascade_path="haarcascade_frontalface_default.xml",
                    confidence_threshold=70):
    """
    Opens webcam and runs real-time face recognition using the trained LBPH model.
    Press ESC to quit.
    """
    # ── Load model ─────────────────────────────────────────────────────────────
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read(model_path)
    except cv2.error:
        print(f"[ERROR] Could not load model from '{model_path}'.")
        print("        Please train the model first (option 2 in main menu).")
        return

    # ── Load Haar Cascade ───────────────────────────────────────────────────────
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(f"[ERROR] Could not load '{cascade_path}'.")
        return

    # ── Open Webcam ─────────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Real-time recognition started. Press ESC to quit.")

    # Font settings
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.9
    thickness  = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]

            # ── Predict ─────────────────────────────────────────────────────────
            student_id, confidence = recognizer.predict(face_roi)

            # Lower confidence = better match in LBPH
            if confidence < confidence_threshold:
                label = get_name(student_id)
                color = (0, 255, 0)   # Green – recognised
                info  = f"{label}  [{int(confidence)}]"
            else:
                label = "Unknown"
                color = (0, 0, 255)   # Red – not recognised
                info  = f"Unknown  [{int(confidence)}]"

            # ── Draw UI ──────────────────────────────────────────────────────────
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Black background pill for text
            text_y = y - 10 if y - 10 > 10 else y + h + 20
            (tw, th), _ = cv2.getTextSize(info, font, font_scale, thickness)
            cv2.rectangle(frame, (x, text_y - th - 4), (x + tw + 6, text_y + 4), color, -1)
            cv2.putText(frame, info, (x + 3, text_y), font, font_scale, (0, 0, 0), thickness)

        cv2.imshow("Smart Attendance – Recognition (ESC to quit)", frame)

        if cv2.waitKey(1) == 27:   # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Recognition session ended.")
