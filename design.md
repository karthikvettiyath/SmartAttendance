# Design Document – Face Module

## 1. System Flow

Webcam → Frame Capture → Grayscale Conversion → Face Detection → Crop → Resize → Save

## 2. Folder Structure

dataset/
    ├── student_id/
          ├── img1.jpg
          ├── img2.jpg

## 3. Detection Algorithm

- Haar Cascade Classifier
- Scale factor: 1.3
- Min neighbors: 5

## 4. Image Processing

- Convert BGR to Grayscale
- Resize to 200x200
- Save as JPG

## 5. Error Handling

- No face detected → Skip frame
- Multiple faces → Capture largest face
