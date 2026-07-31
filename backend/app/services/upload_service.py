import os
import uuid

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
UPLOAD_FOLDER = "uploads/resumes"

def is_allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def save_resume_file(file):
    # Validates and saves an uploaded resume file. Returns the saved path, or raises ValueError.
    if not is_allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Accepted types: {', '.join(ALLOWED_EXTENSIONS)}")

    # Check size by seeking to the end and reading position — avoids loading the whole file into memory
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # reset back to the start so it can actually be read/saved

    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File too large. Max size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.")

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    extension = file.filename.rsplit(".", 1)[1].lower()
    safe_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(file_path)

    return file_path