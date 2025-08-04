# hanifx/qr_unlock.py
import qrcode

def generate_qr(data, filename="qr_code.png"):
    qr_img = qrcode.make(data)
    qr_img.save(filename)
    print(f"[+] QR code saved as {filename}")

def decode_qr(image_path):
    # Decoding QR requires external libraries like OpenCV or pyzbar.
    print("[!] QR decode not implemented. Use OpenCV or pyzbar for this.")
    return None
