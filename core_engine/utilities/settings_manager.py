import json
from pathlib import Path
from typing import Any, Dict

class SettingsManager:
    def __init__(self, config_path: str = "config.json"):
        # إصلاح المسار: الانتقال لمستوى أعلى (المشروع الرئيسي)
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.config_path = self.base_dir / config_path
        self.config = self._load_config()
        self.settings = self._load_all_settings()
    
    
    def _load_config(self) -> Dict[str, Any]:
        """تحميل ملف التكوين الرئيسي"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل ملف التكوين: {e}")
            return {}
    
    def _load_all_settings(self) -> Dict[str, Any]:
        """تحميل جميع ملفات الإعدادات الفرعية"""
        settings = {}
        config_files = self.config.get("config_files", {})
        
        for category, rel_path in config_files.items():
            file_path = self.base_dir / rel_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings[category] = json.load(f)
            except Exception as e:
                print(f"⚠️ تعذر تحميل إعدادات {category}: {e}")
                settings[category] = {}
        
        return settings
    
    def get(self, category: str, key: str, default: Any = None) -> Any:
        """الحصول على قيمة إعداد معينة"""
        return self.settings.get(category, {}).get(key, default)
    
    def get_path(self, path_type: str) -> Path:
        """الحصول على مسار نظام معين"""
        return self.base_dir / self.config.get("paths", {}).get(path_type, "")
    
    def save_setting(self, category: str, key: str, value: Any):
        """حفظ إعداد معين وتحديث الملف"""
        if category in self.settings:
            self.settings[category][key] = value
            self._save_category(category)
    
    def _save_category(self, category: str):
        """حفظ فئة معينة من الإعدادات في ملفها"""
        if category in self.config.get("config_files", {}):
            file_path = self.base_dir / self.config["config_files"][category]
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.settings[category], f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"❌ فشل في حفظ إعدادات {category}: {e}")
    
    def reload(self):
        """إعادة تحميل جميع الإعدادات"""
        self.settings = self._load_all_settings()
    
    def __getitem__(self, key):
        """الوصول المباشر إلى فئات الإعدادات"""
        return self.settings.get(key, {})