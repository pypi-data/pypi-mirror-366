from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import hmac

class BitCrypt:
    def __init__(self):
        self.master_key = b"SecretGroub2Key!"
        self.block_size = 16

    def derive_key(self, iv: bytes) -> bytes:
        derived = hashlib.sha256(self.master_key + iv).digest()
        return derived[:16]

    def encrypt(self, plaintext: bytes) -> bytes:
        iv = get_random_bytes(16)
        key = self.derive_key(iv)
        padded = pad(plaintext, self.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        ciphertext = cipher.encrypt(padded)

        hmac_signature = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()

        return iv + ciphertext + hmac_signature

    def decrypt(self, full_ciphertext: bytes) -> bytes:
        if len(full_ciphertext) < 48:
            raise ValueError("Invalid ciphertext: too short to contain IV and HMAC.")

        hmac_received = full_ciphertext[-32:]
        encrypted_data = full_ciphertext[:-32]
        iv = encrypted_data[:16]
        ct = encrypted_data[16:]
        key = self.derive_key(iv)

        expected_hmac = hmac.new(key, iv + ct, hashlib.sha256).digest()
        if not hmac.compare_digest(hmac_received, expected_hmac):
            raise ValueError("HMAC verification failed. Data may have been tampered with.")

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded = cipher.decrypt(ct)
        plaintext = unpad(padded, self.block_size)
        return plaintext