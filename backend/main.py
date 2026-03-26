from fastapi import FastAPI
from . import models
from .database import engine
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

# Auto-create database tables on startup if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Web Attendance System APIs", description="Backend APIs for the Smart Attendance Project")

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Attendance API. Explore the endpoints at /docs"}
