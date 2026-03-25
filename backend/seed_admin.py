import sys
import os

# Ensure backend imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend import models, auth

def create_admin():
    # Force table creation
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        print("[INFO] Creating default admin user...")
        hashed_password = auth.get_password_hash("admin123")
        new_user = models.User(username="admin", hashed_password=hashed_password, role=models.RoleEnum.Admin)
        db.add(new_user)
        db.commit()
        print("[SUCCESS] Admin user created! Username: admin | Password: admin123")
    else:
        print("[INFO] Admin user already exists. Use Username: admin | Password: admin123")
        
    db.close()

if __name__ == "__main__":
    create_admin()
