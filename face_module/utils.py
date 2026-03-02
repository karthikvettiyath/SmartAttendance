def create_student_directory(student_id):
    """
    Creates a directory for a given student ID inside the 'dataset' folder.
    Returns the path to the directory.
    """
    import os
    dataset_dir = "dataset"
    student_dir = os.path.join(dataset_dir, str(student_id))
    
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
        
    if not os.path.exists(student_dir):
        os.makedirs(student_dir)
        print(f"[INFO] Created directory for student ID {student_id} at {student_dir}")
    else:
        print(f"[INFO] Directory already exists for student ID {student_id}")
        
    return student_dir
