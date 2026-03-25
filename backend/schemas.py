from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StudentBase(BaseModel):
    name: str
    roll_no: str
    department: str

class StudentCreate(StudentBase):
    face_encoding: str # Stored as JSON string

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    student_id: int
    date: date
    session: str
    status: str

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    class Config:
        from_attributes = True
