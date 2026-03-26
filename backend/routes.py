import os
import cv2
import json
import numpy as np
import base64
import io
from PIL import Image, ImageOps
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from deepface import DeepFace
from mtcnn import MTCNN
from . import models, schemas, auth, database

# Needed for bypassing Keras 3 issues on Windows Python 3.12
os.environ["TF_USE_LEGACY_KERAS"] = "1"

router = APIRouter()
detector = MTCNN()

def find_cosine_distance(source_rep, test_rep):
    a = np.matmul(np.transpose(source_rep), test_rep)
    b = np.sum(np.multiply(source_rep, source_rep))
    c = np.sum(np.multiply(test_rep, test_rep))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def base64_to_cv2(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    img_data = base64.b64decode(base64_string)
    pil_img = Image.open(io.BytesIO(img_data))
    pil_img = ImageOps.exif_transpose(pil_img)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return img

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/reports/")
def get_reports(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Fetches all attendance records."""
    records = db.query(models.Attendance).all()
    out = []
    for r in records:
        stud = db.query(models.Student).filter(models.Student.id == r.student_id).first()
        out.append({
            "id": r.id,
            "student_name": stud.name if stud else "Unknown",
            "roll_no": stud.roll_no if stud else "N/A",
            "date": r.date,
            "session": r.session,
            "status": r.status
        })
    return out

@router.post("/students/enroll")
def enroll_student(
    name: str = Form(...), 
    roll_no: str = Form(...), 
    department: str = Form(...),
    images: str = Form(...), # JSON string array of base64 images
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Enrolls a new student using WebRTC Base64 images."""
    db_student = db.query(models.Student).filter(models.Student.roll_no == roll_no).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student already exists")

    image_list = json.loads(images)
    encodings = []

    for idx, b64 in enumerate(image_list):
        img = base64_to_cv2(b64)
        if img is None: continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        try:
            results = DeepFace.represent(rgb, model_name="Facenet512", detector_backend="mtcnn", enforce_detection=False)
            if results:
                # Select the largest face if multiple people are in the webcam
                largest = max(results, key=lambda r: r['facial_area']['w'] * r['facial_area']['h'])
                encodings.append(largest["embedding"])
        except Exception as e:
            print(f"[ERROR] Enrollment extraction failed: {e}")

    if not encodings:
        raise HTTPException(status_code=400, detail=f"No faces could be encoded from the ({len(image_list)}) received frames. Check lighting or angle.")

    # Save multiple encodings for better multi-angle matching
    new_student = models.Student(
        name=name, 
        roll_no=roll_no, 
        department=department, 
        face_encoding=json.dumps(encodings)
    )
    db.add(new_student)
    db.commit()
    return {"message": f"Successfully enrolled {name} with {len(encodings)} face encodings."}

@router.get("/students/")
def get_students(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    students = db.query(models.Student).all()
    return [{"id": s.id, "name": s.name, "roll_no": s.roll_no, "department": s.department} for s in students]

@router.post("/attendance/upload")
def upload_classroom_image(
    file: UploadFile = File(...), 
    session_name: str = Form(...), 
    target_date: date = Form(...),
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """Marks attendance by running DeepFace across a mass classroom photo and returning bounding boxes."""
    # 1. Decode Image and fix Mobile EXIF rotation
    contents = file.file.read()
    pil_img = Image.open(io.BytesIO(contents))
    pil_img = ImageOps.exif_transpose(pil_img)
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 2. Get students and their encodings
    students = db.query(models.Student).all()
    db_encodings_map = {}
    student_info_map = {} # Store both name and roll_no
    for s in students:
        student_info_map[s.id] = {"name": s.name, "roll_no": s.roll_no}
        if s.face_encoding:
            db_encodings_map[s.id] = json.loads(s.face_encoding)

    present_student_ids = set()
    
    # 3. Process the full image via DeepFace natively (which extracts, aligns, and embeds)
    try:
        results = DeepFace.represent(rgb_frame, model_name="Facenet512", detector_backend="mtcnn", enforce_detection=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No structurally sound faces detected in the classroom image.")

    if not results:
        raise HTTPException(status_code=400, detail="No faces detected in the classroom image.")

    # 4. Map the bounding boxes and evaluate threshold
    for res in results:
        encoding = res["embedding"]
        area = res["facial_area"]
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        
        color = (0, 0, 255) # Red for Unknown
        label = "Unknown"
        
        best_match_id = None
        min_dist = float('inf')
        
        # Compare to all multi-angle encodings
        for student_id, st_encs in db_encodings_map.items():
            for st_enc in st_encs:
                st_enc_np = np.array(st_enc)
                encoding_np = np.array(encoding)
                
                # Safety guard: Skip if dimensions don't match (prevents crash on size mismatch)
                if st_enc_np.shape != encoding_np.shape:
                    continue
                    
                dist = find_cosine_distance(st_enc_np, encoding_np)
                if dist < min_dist:
                    min_dist = dist
                    best_match_id = student_id
        
        # Cosine distance threshold verification for Facenet512 (<0.30 is extremely strict)
        if min_dist < 0.30 and best_match_id is not None:
            present_student_ids.add(best_match_id)
            color = (0, 255, 0) # Green for Match
            info = student_info_map[best_match_id]
            label = f"{info['name']} ({info['roll_no']})"
        else:
            label = "Unknown"

        # Graphic plotting
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_y = y - 10 if y - 10 > 10 else y + h + 20
        (tw, th), _ = cv2.getTextSize(label, font, 0.9, 3)
        cv2.rectangle(frame, (x, text_y - th - 5), (x + tw + 5, text_y + 5), color, -1)
        cv2.putText(frame, label, (x + 2, text_y), font, 0.9, (0, 0, 0), 3)

    # 5. Save attendance records to the DB
    new_records = 0
    for sid in present_student_ids:
        # Avoid duplicate marks for same day+session
        exists = db.query(models.Attendance).filter_by(student_id=sid, date=target_date, session=session_name).first()
        if not exists:
            att = models.Attendance(student_id=sid, date=target_date, session=session_name, status="Present")
            db.add(att)
            new_records += 1

    db.commit()
    
    # Encode frame to base64 for frontend viewing
    _, buffer = cv2.imencode('.jpg', frame)
    out_b64 = base64.b64encode(buffer).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{out_b64}"

    return {
        "message": f"Processed {len(results)} faces. Logged {new_records} 'Present' records for {len(present_student_ids)} students.",
        "image": data_uri
    }

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Deletes a student and their face enrollment data."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Also delete associated attendance records
    db.query(models.Attendance).filter(models.Attendance.student_id == student_id).delete()
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@router.patch("/attendance/{attendance_id}")
def update_attendance(attendance_id: int, update_data: schemas.AttendanceUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Updates the status of a specific attendance record."""
    record = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    record.status = update_data.status
    db.commit()
    return {"message": "Attendance updated successfully"}
