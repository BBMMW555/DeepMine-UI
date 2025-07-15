import json
import os
from typing import Dict, List, Any
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


def load_json(file_path):
    try:
        # التأكد من أن file_path هو كائن Path
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في تحميل الملف {file_path}: {e}")
        return None

def save_json(data, file_path):
    try:
        # التأكد من أن file_path هو كائن Path وإنشاء المجلدات
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise IOError(f"فشل في حفظ الملف {file_path}: {str(e)}")

def read_db_file(file_path):
    try:
        # محاولة قراءة كملف ثنائي
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading DB file: {e}")
        return None        