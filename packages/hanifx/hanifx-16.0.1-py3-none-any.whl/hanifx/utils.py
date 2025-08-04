# hanifx/utils.py
import os

def file_exists(path):
    return os.path.isfile(path)

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def write_bytes(path, data):
    with open(path, 'wb') as f:
        f.write(data)
