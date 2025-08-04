# hanifx/self_destruct.py
import os
import time

def self_destruct(file_path, countdown_seconds=10):
    print(f"[!] Self-destruct will activate in {countdown_seconds} seconds...")
    time.sleep(countdown_seconds)
    if os.path.exists(file_path):
        os.remove(file_path)
        print("[+] File has been destroyed.")
    else:
        print("[!] File not found for self-destruction.")
