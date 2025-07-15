from pathlib import Path
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

class AudioResponses:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.sounds = self._load_sounds()
        
    def _load_sounds(self):
        sounds_dir = self.BASE_DIR / "assets" / "sounds"
        return {
            'wake': self._create_sound(sounds_dir / "wake.wav"),
            'success': self._create_sound(sounds_dir / "success.wav"),
            'error': self._create_sound(sounds_dir / "error.wav")
        }
        
    def _create_sound(self, path):
        sound = QSoundEffect()
        if path.exists():
            sound.setSource(QUrl.fromLocalFile(str(path)))
        return sound
        
    def play(self, sound_type):
        if sound_type in self.sounds and self.sounds[sound_type].source().isValid():
            self.sounds[sound_type].play()
