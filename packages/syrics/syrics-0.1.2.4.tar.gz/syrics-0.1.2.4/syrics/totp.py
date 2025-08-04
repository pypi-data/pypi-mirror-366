import hashlib
import hmac
import math
import requests

# thanks to https://github.com/glomatico/votify/blob/main/votify/totp.py
class TOTP:
    def __init__(self) -> None:
        self.secret, self.version = self.get_secret_version()
        self.period = 30
        self.digits = 6

    def generate(self, timestamp: int) -> str:
        counter = math.floor(timestamp / 1000 / self.period)
        counter_bytes = counter.to_bytes(8, byteorder="big")

        h = hmac.new(self.secret, counter_bytes, hashlib.sha1)
        hmac_result = h.digest()

        offset = hmac_result[-1] & 0x0F
        binary = (
            (hmac_result[offset] & 0x7F) << 24
            | (hmac_result[offset + 1] & 0xFF) << 16
            | (hmac_result[offset + 2] & 0xFF) << 8
            | (hmac_result[offset + 3] & 0xFF)
        )

        return str(binary % (10**self.digits)).zfill(self.digits)
    
    def get_secret_version(self) -> tuple[str, int]:
        req = requests.get("https://raw.githubusercontent.com/Thereallo1026/spotify-secrets/refs/heads/main/secrets/secrets.json")
        if req.status_code != 200:
            raise ValueError("Failed to fetch TOTP secret and version.")
        data = req.json()[-1]
        ascii_codes = [ord(c) for c in data['secret']]
        transformed = [val ^ ((i % 33) + 9) for i, val in enumerate(ascii_codes)]
        secret_key = "".join(str(num) for num in transformed)
        return bytes(secret_key, 'utf-8'), data['version']