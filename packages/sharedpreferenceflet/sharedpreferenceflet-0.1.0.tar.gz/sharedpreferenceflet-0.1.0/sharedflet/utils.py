
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
import os
class cryptographyJson:
    @staticmethod
    def encrypt_file_advanced(file_path, key):
        cipher = AES.new(key, AES.MODE_EAX)
        with open(file_path, 'rb') as file:
            data = file.read()

        ciphertext, tag = cipher.encrypt_and_digest(data)

        with open(file_path + '.lock', 'wb') as file:
            file.write(cipher.nonce + tag + ciphertext)

        os.remove(file_path)

    @staticmethod
    def decrypt_file(encrypted_path, key):
        with open(encrypted_path, 'rb') as file:
            nonce = file.read(16)
            tag = file.read(16)
            ciphertext = file.read()

        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        original_path = encrypted_path[:-5]
        with open(original_path, 'wb') as file:
            file.write(data)

        os.remove(encrypted_path)
