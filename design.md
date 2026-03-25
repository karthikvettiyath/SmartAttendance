# System Design Document

## System Flow

1. Teacher uploads classroom image
2. Backend detects faces
3. Faces are encoded into vectors
4. Compare with database encodings
5. Mark matched students as present
6. Mark others as absent

## Dataset Design

- Each student has 50–100 images
- Multiple angles included
- Encodings stored in database

## UI Design

- Login Page
- Dashboard (based on role)
- Upload Attendance Page
- Reports Page

## Recognition Logic

- Face distance threshold: 0.6
- Best match selected

## Error Handling

- No faces detected → notify user
- Unknown faces → ignore
