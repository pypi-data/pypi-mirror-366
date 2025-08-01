# hanifx/utils.py
import os
import random
import string
import time

def show_warning():
    print("\n⚠️  WARNING:")
    print("Once you encrypt this file, it will be IMPOSSIBLE to decrypt it.")
    print("Continue only if you're 100% sure.\n")
    time.sleep(1)

def get_extension(path):
    return os.path.splitext(path)[1].lower()

def random_string(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
