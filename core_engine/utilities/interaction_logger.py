from typing import Dict
import json
import os
from datetime import datetime
from core_engine.utilities.file_utils import save_json

class InteractionLogger:
    def __init__(self, log_file: str = 'logs/interactions.json'):
        self.log_file = log_file
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """إنشاء ملف السجل إذا لم يكن موجودًا"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            save_json(self.log_file, [])
    
    def log_interaction(self, command: str, response: Dict):
        """تسجيل تفاعل جديد"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': response,
            'session_id': self._get_session_id()
        }
        save_json(self.log_file, entry, append=True)
    
    def log_error(self, error_message: str):
        """تسجيل خطأ جديد"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error_message,
            'session_id': self._get_session_id()
        }
        save_json('logs/errors.json', error_entry, append=True)
    
    def _get_session_id(self) -> str:
        """إنشاء معرف جلسة فريد"""
        return datetime.now().strftime("%Y%m%d%H%M%S")