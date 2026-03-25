from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum

class RoleEnum(enum.Enum):
    Admin = "Admin"
    Principal = "Principal"
    HOD = "HOD"
    Teacher = "Teacher"
    Student = "Student"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.Teacher)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    roll_no = Column(String(50), unique=True, index=True)
    department = Column(String(50))
    # We will store the 128D encoding array as a JSON string
    face_encoding = Column(Text) 

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date)
    session = Column(String(50)) # e.g. 'Morning', 'Forenoon', etc.
    status = Column(String(20)) # 'Present' or 'Absent'

    student = relationship("Student")
