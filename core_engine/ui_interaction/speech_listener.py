# core_engine.ui_interaction.speech_listener.py

from PyQt5.QtCore import QObject, pyqtSignal

class SpeechListener(QObject):
    def __init__(self, speech_engine, parent=None):
        super().__init__(parent)
        
        self.speech_engine = speech_engine
        self.is_listening = False

    def start_listening(self):
        """بدء الاستماع الصوتي"""
        if not self.is_listening:
            self.speech_engine.start_listening(self._on_command_received)
            self.is_listening = True

    def stop_listening(self):
        """إيقاف الاستماع الصوتي"""
        if self.is_listening:
            self.speech_engine.stop_listening()
            self.is_listening = False

    def _on_command_received(self, command):
        """معالجة الأوامر المستلمة"""
        if command.strip():
            self.command_received.emit(command)