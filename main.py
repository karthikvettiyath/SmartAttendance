import os
import sys
from face_module.utils import create_student_directory
from face_module.capture import capture_student_faces
from face_module.preprocess import preprocess_images

def capture_mode():
    if not os.path.exists("haarcascade_frontalface_default.xml"):
        print("[ERROR] haarcascade_frontalface_default.xml not found!")
        return

    student_id = input("\nEnter Student ID: ").strip()
    if not student_id:
        print("[ERROR] Invalid Student ID.")
        return

    target_dir = create_student_directory(student_id)

    print("\n>>> Phase 1: Capturing Face Images")
    success = capture_student_faces(student_id, target_dir, num_images=50)

    if not success:
        print("[ERROR] Capture phase incomplete. Aborting preprocessing.")
        return

    print("\n>>> Phase 2: Preprocessing Images")
    preprocess_images(target_dir)
    print(f"\n[INFO] Dataset ready for student: {student_id}")

def train_mode():
    from trainer.train import train_model
    train_model(dataset_dir="dataset", model_output_path="trainer/model.yml")

def recognize_mode():
    from face_module.recognize import run_recognition
    run_recognition()

def main():
    print("========================================")
    print("       Smart Attendance System          ")
    print("========================================")
    print(" 1. Capture New Student Dataset")
    print(" 2. Train Face Recognition Model")
    print(" 3. Run Real-Time Recognition")
    print(" 4. Exit")
    print("========================================")

    choice = input("\nSelect option (1/2/3/4): ").strip()

    if choice == "1":
        capture_mode()
    elif choice == "2":
        train_mode()
    elif choice == "3":
        recognize_mode()
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("[ERROR] Invalid option.")

if __name__ == "__main__":
    main()
