import os
import json
import pyaudio
import vosk
from threading import Thread
from queue import Queue
from PyQt5.QtCore import QObject, pyqtSignal
from core_engine.utilities.logger import log_system_event
from core_engine.utilities.file_utils import load_json

from core_engine.audio_responses import AudioResponses
# core_engine/speech_processing/speech_manager.py

class SpeechManager(QObject):
    command_detected = pyqtSignal(str)
    

    def __init__(self, model_path=None, config=None):
        super().__init__()
        
        # تحديد المسار الأساسي للمشروع
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # استخدام model_path إذا تم تمريره، وإلا نستخدم النموذج الافتراضي
        if model_path is None:
            # افتراضي: نموذج العربي
            model_path = os.path.join(self.BASE_DIR, "models", "vosk-model-ar-0.22-linto-1.1.0")
        self.model_path = model_path
        self.config = config or {}
        self.audio_queue = Queue()
        self.recognition_thread = None
        self._is_listening = False  # نستخدم شرطة سفلية لتجنب التعارض مع اسم الدالة
        
        # تهيئة نظام الصوت
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # تحميل كلمات التنبيه
        self.wake_words = self.load_wake_words()
        
        # التحقق من وجود النموذج
        if not os.path.exists(self.model_path):
            log_system_event(f"Model not found: {self.model_path}", level='error')
            raise FileNotFoundError(f"Model directory not found: {self.model_path}")
        
        # تحميل النموذج
        try:
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            log_system_event(f"Speech model loaded: {self.model_path}")
        except Exception as e:
            log_system_event(f"Failed to load speech model: {str(e)}", level='error')
            raise

        # إنشاء stream الصوت
        self.create_audio_stream()
        self.audio_responses = AudioResponses()

    def create_audio_stream(self):
        """تهيئة تدفق الصوت"""
        if self.stream is None:
            try:
                self.stream = self.p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192,
                    stream_callback=self.audio_callback
                )
            except Exception as e:
                log_system_event(f"Failed to create audio stream: {str(e)}", level='error')
                raise

    def is_listening(self):
        """التحقق مما إذا كان النظام يستمع حاليًا"""
        return self._is_listening

    def load_wake_words(self):
        try:
            config_path = os.path.join(self.BASE_DIR, "config", "wake_word_settings.json")
            settings = load_json(config_path)
            
            # دمج wake_words الأساسية مع الأسماء المخصصة
            base_words = settings.get("wake_words", ["يا مساعد", "يا deepmine","مساعد","تيب ميني","deepmine"])
            custom_aliases = settings.get("aliases", [])
            
            return base_words + custom_aliases
        except Exception as e:
            log_system_event(f"Failed to load wake words: {str(e)}", level='warning')
            return ["يا مساعد", "يا deepmine","مساعد","تيب ميني","deepmine"]

    def audio_callback(self, in_data, frame_count, time_info, status):
        """دالة رد الاتصال لالتقاط الصوت"""
        if self._is_listening:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def start_listening(self, callback=None):
        """بدء الاستماع للأوامر الصوتية"""
        self._is_listening = True
        if self.stream is None:
            self.create_audio_stream()
        self.stream.start_stream()
        
        # تشغيل صوت التنبيه
        self.audio_responses.play('wake')

        # إنشاء تدفق الصوت إذا لم يكن موجودًا
        if self.stream is None:
            self.create_audio_stream()
            
        self._is_listening = True
        self.stream.start_stream()
        log_system_event("Microphone activated, waiting for commands")
        
        # بدء خيط التعرف فقط إذا تم توفير callback
        if callback:
            self.recognition_thread = Thread(target=self.process_audio)
            self.recognition_thread.daemon = True
            self.recognition_thread.start()

    def stop_listening(self):
        """إيقاف الاستماع"""
        self._is_listening = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
            except:
                pass
            
        self.audio_queue.queue.clear()
        log_system_event("Microphone deactivated")


    def process_audio(self):
        """معالجة الصوت والتعرف على الكلام"""
        while self._is_listening:
            try:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        log_system_event(f"Recognized: {text}")
                        
                        # التحقق من وجود كلمة تنبيه
                        wake_detected = any(
                            wake_word.lower() in text.lower() 
                            for wake_word in self.wake_words
                        )
                        
                        if wake_detected:
                            # استخراج الأمر الفعلي
                            command = self.extract_command(text)
                            # استخدام الإشارة بدلاً من callback
                            self.command_detected.emit(command)
                            
            except Exception as e:
                log_system_event(f"Recognition error: {str(e)}", level='error')

    def extract_command(self, text):
        """استخراج الأمر بعد كلمة التنبيه"""
        text_lower = text.lower()
        for wake_word in self.wake_words:
            wake_lower = wake_word.lower()
            if wake_lower in text_lower:
                # إزالة كلمة التنبيه فقط عند بداية الجملة
                if text_lower.startswith(wake_lower):
                    return text[len(wake_word):].strip()
        return text

    def __del__(self):
        """تنظيف الموارد عند التدمير"""
        try:
            self.stop_listening()
            
            if self.stream:
                try:
                    self.stream.close()
                except:
                    pass
                self.stream = None
                
            if self.p:
                try:
                    self.p.terminate()
                except:
                    pass
                self.p = None
                
        except Exception as e:
            log_system_event(f"Error in cleanup: {str(e)}", level='warning')
            
        log_system_event("Speech recognition resources cleaned")

    #-----------------تحميل إعدادات كلمة التنبيه-----------------
    def load_wake_settings(self):
        """تحميل إعدادات كلمة التنبيه من ملف JSON"""
        config_path = self.BASE_DIR / "config" / "wake_word_settings.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('wake_word', {}).get('phrases', [])
        except Exception as e:
            print(f"Failed to load wake words: {e}")
            return ["يا مساعد", "يا ميني"]     