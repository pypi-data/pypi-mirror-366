# hanifx/core.py
import os
from .utils import show_warning, get_extension, random_string
from .langmap import EXTENSION_MAP
from .engine import python_enc, java_enc, php_enc, c_enc

def encrypt_file(filepath):
    ext = get_extension(filepath)
    show_warning()

    if ext not in EXTENSION_MAP:
        raise Exception(f"Unsupported file extension: {ext}")

    lang = EXTENSION_MAP[ext]

    if lang == "python":
        python_enc.encrypt(filepath)
    elif lang == "java":
        java_enc.encrypt(filepath)
    elif lang == "php":
        php_enc.encrypt(filepath)
    elif lang == "c":
        c_enc.encrypt(filepath)
    else:
        raise Exception(f"No encryption engine found for: {lang}")
