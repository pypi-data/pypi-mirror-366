# hanifx

A modern encryption module designed with future features like fake decrypt, geo lock, telegram unlock, self-destruct, and QR-based unlock.

## Installation

```bash
pip install hanifx

# from hanifx import HanifxCore 

h = HanifxCore()
print(h.get_key())

h.encrypt_file("file.txt", "file.enc")
h.decrypt_file("file.enc", "file.dec.txt")
