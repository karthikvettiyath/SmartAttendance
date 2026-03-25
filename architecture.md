# System Architecture

## High-Level Architecture

Frontend (Web App)
        ↓
Backend API (Flask/FastAPI)
        ↓
Face Recognition Engine
        ↓
Database (MySQL)

## Modules

1. Authentication Module
2. Dataset Creation Module
3. Face Recognition Module
4. Attendance Management Module
5. Reporting Module

## Data Flow

User → Upload Image → Backend → Face Detection → Matching → Attendance Update → Response

## Integration

- REST API connects frontend and backend
- Face recognition runs server-side
