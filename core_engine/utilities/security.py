from cryptography.fernet import Fernet
import base64
import os

class SecurityManager:
    def __init__(self, key_file: str = 'data/security.key'):
        self.key = self._load_or_generate_key(key_file)
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self, key_file: str) -> bytes:
        """تحميل أو توليد مفتاح التشفير"""
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt(self, data: str) -> str:
        """تشفير البيانات"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data: str) -> str:
        """توليد هاش للبيانات الحساسة"""
        return base64.b64encode(data.encode()).decode()