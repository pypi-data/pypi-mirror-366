# hanifx/geo_lock.py
import socket

# List of allowed IPs or IP ranges
ALLOWED_IPS = ["127.0.0.1"]  # Example localhost only

def get_current_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "0.0.0.0"

def is_ip_allowed():
    current_ip = get_current_ip()
    return current_ip in ALLOWED_IPS
