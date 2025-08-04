# hanifx/core.py

from cryptography.fernet import Fernet

class HanifxCore:
    def __init__(self, key=None):
        if key is None:
            self.key = Fernet.generate_key()
        else:
            if isinstance(key, bytes):
                self.key = key
            else:
                self.key = key.encode()
        self.cipher = Fernet(self.key)

    def get_key(self):
        return self.key.decode()

    def encrypt_file(self, input_path, output_path):
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted_data = self.cipher.encrypt(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        print(f"[+] File encrypted successfully: {output_path}")

    def decrypt_file(self, input_path, output_path):
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            print(f"[+] File decrypted successfully: {output_path}")
        except Exception as e:
            print(f"[!] Decryption failed: {e}")
