# core_engine.ui_interaction.interaction_manager.py

from PyQt5.QtCore import QObject, pyqtSignal

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtMultimedia import QSoundEffect
from pathlib import Path
import json
import winsound

class InteractionManager(QObject):
    command_received = pyqtSignal(str, dict)  # إشارة معدلة لتشمل البيانات الإضافية
    assistant_ready = pyqtSignal()
    audio_played = pyqtSignal(str)  # إشارة جديدة لتتبع تشغيل الأصوات
    
    def __init__(self, text_manager, speech_engine, parent=None):
        super().__init__(parent)
        self.text_manager = text_manager
        self.speech_engine = speech_engine
        self.current_command = ""
        self.wake_words = self._load_wake_words()
        self.sound_effects = self._init_sound_effects()
        
    def _load_wake_words(self):
        """تحميل كلمات التنبيه من ملف الإعدادات"""
        try:
            config_path = Path(__file__).resolve().parent.parent.parent / "config" / "wake_word_settings.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('wake_word', {}).get('phrases', ["يا مساعد", "يا ميني"])
        except Exception as e:
            print(f"خطأ في تحميل كلمات التنبيه: {str(e)}")
            return ["يا مساعد", "يا ميني"]
    
    def _init_sound_effects(self):
        """تهيئة المؤثرات الصوتية"""
        sounds = {
            'wake': self._create_sound("wake.wav"),
            'response': self._create_sound("response.wav"),
            'error': self._create_sound("error.wav")
        }
        return sounds
    
    def _create_sound(self, filename):
        """إنشاء مؤثر صوتي من ملف"""
        sound = QSoundEffect()
        sound_path = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds" / filename
        if sound_path.exists():
            sound.setSource(QUrl.fromLocalFile(str(sound_path)))
        return sound
