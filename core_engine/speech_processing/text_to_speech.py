import os
import pyttsx3
from PyQt5.QtCore import QObject, pyqtSignal
from pathlib import Path
from core_engine.utilities.file_utils import load_json
from core_engine.utilities.logger import log_system_event

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).parent.parent.parent

class TextToSpeech:
    def __init__(self, config_path="config/ui_settings.json"):
        self.config = self.load_config(config_path)
        self.engine = self.init_engine()
        self.set_voice(voice)
        self.set_speed(speed)
        
    def load_ui_config(self, config_path):
        """تحميل إعدادات الصوت"""
        config_file = BASE_DIR / ui_settings_path
        default_ui_config = {
            "preferred_voice": "female",
            "language": "ar",
            "voice_volume": 80,
            "voice_rate": 150,
            "voice_pitch": 50
        }
        
        try:
            if config_file.exists():
                return load_json(ui_config_file)
        except Exception as e:
            log_system_event(f"Error loading TTS ui_config: {str(e)}", level='error')
        
        return default_config
    
    def init_engine(self):
        """تهيئة محرك تحويل النص إلى كلام"""
        try:
            engine = pyttsx3.init()
           
            

            # تحديد الصوت حسب التفضيل
            voices = engine.getProperty('voices')
            voice_found = False
            
            # البحث عن الصوت المفضل
            for voice in voices:
                voice_gender = "female" if "female" in voice.name.lower() else "male"
                
                if voice_gender == self.config.get("preferred_voice", "female"):
                    engine.setProperty('voice', voice.id)
                    voice_found = True
                    log_system_event(f"Using voice: {voice.name}")
                    break
            
            # إذا لم يتم العثور على الصوت المفضل
            if not voice_found and voices:
                engine.setProperty('voice', voices[0].id)
                log_system_event(f"Using default voice: {voices[0].name}")
            
            # ضبط إعدادات الصوت
            engine.setProperty('volume', self.config.get("voice_volume", 80) / 100)
            engine.setProperty('rate', self.config.get("voice_rate", 150))
            
            return engine
            
        except Exception as e:
            log_system_event(f"Failed to initialize TTS engine: {str(e)}", level='error')
            return None

    def set_voice(self, voice_type):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_type == "male" and "male" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
            elif voice_type == "female" and "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def set_speed(self, speed):
        self.engine.setProperty('rate', speed)

    def speak(self, text: str):
        """تحويل النص إلى كلام"""
        if not self.engine:
            log_system_event("TTS engine not initialized", level='warning')
            return
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            log_system_event(f"Error in TTS: {str(e)}", level='error')
    
    def update_settings(self, new_config: dict):
        """تحديث إعدادات الصوت"""
        self.config.update(new_config)
        self.engine = self.init_engine()