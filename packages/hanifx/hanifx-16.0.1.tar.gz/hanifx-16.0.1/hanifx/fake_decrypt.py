# hanifx/fake_decrypt.py

def verify_password(input_password, real_password):
    return input_password == real_password

def get_fake_file_content():
    return b"This is fake content shown on wrong password!"
