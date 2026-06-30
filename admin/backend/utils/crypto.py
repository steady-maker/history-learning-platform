import base64
from Crypto.Cipher import AES
from history_admin_backend.settings import AES_KEY_b64, AES_IV_b64

def aes_encrypt(text: str) -> str:
    """AES-CBC 加密，返回 base64 字符串"""
    cipher = AES.new(base64.b64decode(AES_KEY_b64), AES.MODE_CBC, base64.b64decode(AES_IV_b64))
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encrypted = cipher.encrypt(text.encode())
    return base64.b64encode(encrypted).decode()

def aes_decrypt(enc: str) -> str:
    """AES-CBC 解密 base64 字符串"""
    cipher = AES.new(base64.b64decode(AES_KEY_b64), AES.MODE_CBC, base64.b64decode(AES_IV_b64))
    data = cipher.decrypt(base64.b64decode(enc))
    pad = data[-1]
    return data[:-pad].decode()