# Product Requirements Document (PRD)
## Module: Face Capture & Dataset Creation

### 1. Overview
This module captures student face images using webcam and stores them in a structured dataset format for training the recognition model.

### 2. Objective
- Capture high-quality face images.
- Detect faces accurately.
- Store images in organized folder structure.

### 3. Functional Requirements
- Open webcam feed.
- Detect face using Haar Cascade.
- Draw bounding box around detected face.
- Capture 50 images per student.
- Convert to grayscale.
- Resize images to 200x200.
- Save inside dataset/student_id folder.

### 4. Non-Functional Requirements
- Fast detection (<1 second delay)
- Works in classroom lighting
- Simple CLI interaction

### 5. Success Criteria
- 95% face detection success in controlled lighting.
- Dataset correctly structured.
