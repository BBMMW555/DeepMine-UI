from pathlib import Path
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl
import json

class AudioResponses:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.sounds = {
            'wake': None,
            'success': None,
            'error': None
        }
        self.load_sounds()
        
    def load_sounds(self):
        """تحميل ملفات الصوت من مجلد assets/sounds"""
        sounds_dir = self.BASE_DIR / "assets" / "sounds"
        
        # تحميل أصوات التنبيه
        self.sounds['wake'] = self._load_sound(sounds_dir / "wake.wav")
        self.sounds['success'] = self._load_sound(sounds_dir / "success.wav")
        self.sounds['error'] = self._load_sound(sounds_dir / "error.wav")
        
        
    def _load_sound(self, path):
        """تحميل ملف صوتي واحد"""
        if path.exists():
            sound = QSoundEffect()
            sound.setSource(QUrl.fromLocalFile(str(path)))
            return sound
        return None
        
    def play(self, sound_type):
        """تشغيل الصوت المطلوب"""
        if sound_type in self.sounds and self.sounds[sound_type]:
            self.sounds[sound_type].play()