import glob
from datetime import datetime

def get_files_from_dist():
    files = glob.glob("dist/*.whl") + glob.glob("dist/*.tar.gz")
    return files

def log_upload(filename, status):
    with open("upload.log", "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] {status}: {filename}\n")
