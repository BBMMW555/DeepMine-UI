from datetime import datetime
from typing import List, Dict, Optional

class ContextManager:
    def __init__(self, max_context=5):
        self.context: List[Dict] = []
        self.max_context = max_context
        
    def add_context(self, context_type: str, data: Dict):
        """إضافة سياق جديد"""
        if len(self.context) >= self.max_context:
            self.context.pop(0)
        self.context.append({
            "type": context_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
    def handle_context(self, current_command: str, command_history: List[Dict]) -> Optional[Dict]:
        """معالجة السياق بناءً على الأمر الحالي"""
        if not self.context:
            return None

        last_cmd = self.context[-1]
        repeat_phrases = ["مرة أخرى", "كرر", "أعد", "أعِد"]
        
        # معالجة طلبات التكرار
        if any(p in current_command for p in repeat_phrases):
            return self._handle_repeat_request(last_cmd)
            
        # معالجة أسئلة المتابعة
        if "نعم" in current_command or "لا" in current_command:
            return self._handle_followup_response(current_command, last_cmd)
            
        return None

    def _handle_repeat_request(self, last_cmd: Dict) -> Optional[Dict]:
        if last_cmd['type'] == 'reply':
            return {
                'type': 'reply',
                'data': last_cmd['data']
            }
        elif last_cmd['type'] == 'execute_app':
            return {
                'type': 'repeat_command',
                'data': last_cmd['data']
            }
        return None

    def _handle_followup_response(self, response: str, last_cmd: Dict) -> Optional[Dict]:
        """معالجة ردود المستخدم على أسئلة المتابعة"""
        if last_cmd['type'] == 'confirmation_needed':
            if "نعم" in response:
                return {'type': 'execute_confirmed', 'data': last_cmd['data']}
            else:
                return {'type': 'action_canceled', 'data': {'message': 'تم إلغاء الإجراء'}}
        return None