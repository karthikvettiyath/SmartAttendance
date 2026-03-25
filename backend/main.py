from fastapi import FastAPI
from . import models
from .database import engine
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

# Auto-create database tables on startup if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Web Attendance System APIs", description="Backend APIs for the Smart Attendance Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Attendance API. Explore the endpoints at /docs"}
