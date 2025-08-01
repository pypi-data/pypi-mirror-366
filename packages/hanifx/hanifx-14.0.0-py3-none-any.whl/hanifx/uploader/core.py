import os
import glob
import requests
from .utils import log_upload, get_files_from_dist

PYPI_UPLOAD_URL = "https://upload.pypi.org/legacy/"

def upload_to_pypi(token: str, files: list):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    success_files = []
    failed_files = []

    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"[X] File not found: {file_path}")
            failed_files.append(file_path)
            continue
        
        with open(file_path, "rb") as f:
            filename = os.path.basename(file_path)
            print(f"[~] Uploading {filename} ...")
            response = requests.post(
                PYPI_UPLOAD_URL,
                data={":action": "file_upload", "protocol_version": "1"},
                files={"content": (filename, f)},
                headers=headers,
            )
            if response.status_code == 200:
                print(f"[✓] Successfully uploaded {filename}")
                success_files.append(filename)
                log_upload(filename, "SUCCESS")
            else:
                print(f"[X] Failed to upload {filename}: {response.status_code}")
                print("Response:", response.text)
                failed_files.append(filename)
                log_upload(filename, f"FAILED {response.status_code}")

    return success_files, failed_files
