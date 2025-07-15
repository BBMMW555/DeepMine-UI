#c:/Users/bassam/Desktop/DeepMine/core_engine/command_processing/command_handler.py
from typing import Dict, List, Optional
from datetime import datetime
from core_engine.utilities.interaction_logger import InteractionLogger
from core_engine.context_manager import ContextManager
from core_engine.command_processing.reply_router import ReplyRouter

class CommandHandler:
    def __init__(self, context_manager=None):
        self.reply_router = ReplyRouter()
        self.context_manager = context_manager or ContextManager()
        self.logger = InteractionLogger()
        self.command_history: List[Dict] = []

    def handle(self, command: str) -> Dict:
        """معالجة الأمر الصوتي وتحليل السياق والنبرة وتنفيذ الرد"""
        # التنظيف الأولي للأمر
        command = command.strip()
        clean_cmd = self._clean_command(command)
        lower_cmd = clean_cmd.lower()
        
        # التحليل الأساسي
        self._log_command(command)
        tone = self._analyze_tone(command)
        
        # 1. التحقق من الأوامر الأساسية المباشرة
        if not clean_cmd or lower_cmd in ["مرحبا", "اهلا", "السلام عليكم"]:
            return {
                'type': 'reply',
                'data': {'message': 'مرحباً بك! كيف يمكنني مساعدتك اليوم؟'},
                'tone': tone
            }
        
        if any(x in lower_cmd for x in ["فتح الإعدادات", "نافذة الإعدادات", "الإعدادات"]):
            self.open_settings()
            return {
                'type': 'action',
                'data': {'message': 'تم فتح نافذة الإعدادات', 'action': 'open_settings'},
                'tone': tone
            }
        
        # 2. معالجة السياق السابق (إذا كان هناك محادثة جارية)
        context_response = self.context_manager.handle_context(clean_cmd, self.command_history)
        if context_response:
            context_response['tone'] = tone
            return context_response
        
        # 3. البحث في الردود الجاهزة
        reply = self.reply_router.find_reply(clean_cmd)
        if reply:
            self.context_manager.add_context('reply', reply)
            return {
                'type': 'reply',
                'data': reply,
                'tone': tone
            }
        
        # 4. تنفيذ الأوامر البرمجية
        executable_response = self._handle_executable_command(clean_cmd, tone)
        if executable_response:
            return executable_response
        
        # 5. إضافة الأمر للتعلم المستقبلي إذا لم يتم التعرف عليه
        self._add_to_pending_learning(clean_cmd)
        
        return {
            'type': 'unknown',
            'data': {
                'message': 'لم أفهم الأمر، سأحفظه للتعلم لاحقًا',
                'original_command': command
            },
            'tone': tone
        }

    def _analyze_tone(self, text: str) -> Dict:
        polite_phrases = ["من فضلك", "لو سمحت", "رجاء", "إذا ممكن"]
        urgent_phrases = ["بسرعة", "عاجل", "الآن", "فوراً"]
        emotional_phrases = ["أرجوك", "أنا بحاجة", "مهم جداً"]
        
        return {
            'politeness': any(p in text for p in polite_phrases),
            'urgency': any(u in text for u in urgent_phrases),
            'emotional': any(e in text for e in emotional_phrases)
        }

    def _handle_executable_command(self, command: str, tone: Dict) -> Optional[Dict]:
        if "افتح" in command or "شغل" in command:
            app_name = command.replace("افتح", "").replace("شغل", "").strip()
            self.context_manager.add_context('execute_app', app_name)
            return {
                'type': 'execute_app',
                'data': {
                    'app': app_name,
                    'status': 'pending'
                },
                'tone': tone
            }
        elif "أنشئ" in command or "اصنع" in command:
            return self._handle_creation_command(command, tone)
        return None

    def _handle_creation_command(self, command: str, tone: Dict) -> Optional[Dict]:
        # يمكنك إضافة منطقك هنا لمعالجة أوامر الإنشاء
        return None

    def _add_to_pending_learning(self, command: str):
        from core_engine.utilities.file_utils import load_json, save_json
        try:
            pending_data = load_json('data/pending_learning.json') or []
            new_entry = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            pending_data.append(new_entry)
            save_json('data/pending_learning.json', pending_data)
        except Exception as e:
            self.logger.log_error(f"فشل في حفظ الأمر للتعلم: {str(e)}")

    def _clean_command(self, command: str) -> str:
        words_to_remove = ["من فضلك", "لو سمحت", "هل يمكنك", "إذا ممكن"]
        for word in words_to_remove:
            command = command.replace(word, "")
        return command.strip()

    def _log_command(self, command: str):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': None
        }
        self.command_history.append(entry)
        self.logger.log_interaction(command, {})