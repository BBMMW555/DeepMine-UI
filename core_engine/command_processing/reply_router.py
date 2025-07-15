import json
import os
from datetime import datetime
from typing import Dict, Tuple, Optional, Callable

class ReplyRouter:
    def __init__(self, user_name: Optional[str] = ""):
        self.user_name = user_name
        self.replies = self._load_static_replies()
      
        self.dynamic_handlers = {
            'dynamic_time': self._handle_time,
            'dynamic_date': self._handle_date,
            'dynamic_weather': self._handle_weather,
            'dynamic_news': self._handle_news,
            'dynamic_schedule': self._handle_schedule
        }
        self.synonyms = {  # <-- إضافة جديدة
            'time': ['الوقت', 'التوقيت', 'الساعة', 'الزمن'],
            'reminder': ['تذكير', 'ذكرني', 'منبه', 'موعد']
        }

    


    def _load_static_replies(self) -> Dict:
        """تحميل الردود الثابتة من ملف JSON"""
        try:
            with open('data/conversation_patterns/static_replies.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل الردود: {e}")
            return {}

    def _handle_time(self) -> Tuple[str, str]:
        """معالجة طلبات الوقت"""
        now = datetime.now().strftime("%I:%M %p")
        return (f"الساعة الآن {now}", f"The time is {now}")

    def _handle_date(self) -> Tuple[str, str]:
        """معالجة طلبات التاريخ"""
        today = datetime.now().strftime("%Y-%m-%d")
        return (f"تاريخ اليوم هو {today}", f"Today's date is {today}")

    def _handle_weather(self) -> Tuple[str, str]:
        """معالجة طلبات الطقس"""
        return ("الطقس اليوم مشمس بدرجة 28°C", "Today's weather is sunny with 28°C")

    def _handle_news(self) -> Tuple[str, str]:
        """معالجة طلبات الأخبار"""
        return ("آخر الأخبار: تطوير مساعد DeepMine بنجاح", "Latest news: DeepMine assistant developed successfully")

    def _handle_schedule(self) -> Tuple[str, str]:
        """معالجة طلبات الجدول اليومي"""
        return ("جدولك اليوم: اجتماع الساعة 10 صباحاً", "Your schedule: Meeting at 10 AM")

    def find_reply(self, user_input: str) -> Optional[Dict]:
        """
        البحث عن رد مناسب للأمر الصوتي مع دعم المطابقة الجزئية
        الإرجاع:
            {
                "text_ar": النص العربي للعرض,
                "text_en": النص الإنجليزي للنطق,
                "type": نوع الرد ("static" أو "dynamic_xx")
            }
        """
        user_input = user_input.lower().strip()
     
        best_match = None
        best_score = 0
     
        for pattern, reply_data in self.replies.items():
            pattern_lower = pattern.lower()
            score = self._calculate_match_score(user_input, pattern_lower)
     
            if score > best_score:
                best_score = score
                best_match = (pattern, reply_data)
     
        if best_match and best_score > 0.5:
            pattern, reply_data = best_match
     
            if 'response_type' in reply_data and reply_data['response_type'] in self.dynamic_handlers:
                handler = self.dynamic_handlers[reply_data['response_type']]
                text_ar, text_en = handler()
            else:
                text_ar = reply_data.get('response_ar', '')
                text_en = reply_data.get('response_en', '')
     
            # ✅ استبدال الاسم {name} إن وُجد
            if hasattr(self, 'user_name') and self.user_name:
                text_ar = text_ar.replace("{name}", self.user_name)
                text_en = text_en.replace("{name}", self.user_name)
     
            return {
                "text_ar": text_ar,
                "text_en": text_en,
                "type": reply_data.get('response_type', 'static')
            }
     
        return None

    def _calculate_match_score(self, user_input: str, pattern: str) -> float:
        """إصدار محسن من دالة المطابقة"""
        # مطابقة المرادفات
        for category, words in self.synonyms.items():
            if category in pattern.lower() and any(w in user_input for w in words):
                return 1.0
                
        # المطابقة الأصلية
        if pattern in user_input:
            return 1.0
        elif any(word in user_input.split() for word in pattern.split()):
            return 0.8  # <-- تعديل قيمة المطابقة الجزئية
        
        return 0.0

    # إضافة وظيفة جديدة
    def get_related_commands(self, command_type: str) -> list:
        """الحصول على أوامر مرتبطة بنوع معين"""
        return [cmd for cmd, data in self.replies.items() 
               if data.get('response_type', '') == command_type]

#--------------------ستخرج اسم المستخدم مع الرد-----------------------------

    def load_user_name():
        try:
            with open("config/user_preferences.json", encoding="utf-8") as f:
                profile = json.load(f)
                return profile.get("name_ar", "")
        except:
            return ""           
              
# اختبار محسن
if __name__ == "__main__":
    router = ReplyRouter()
    
    # إضافة بعض الردود للاختبار إذا كان الملف فارغًا
    router.replies.update({
        "كم الساعة": {
            "response_type": "dynamic_time",
            "response_ar": "",
            "response_en": ""
        },
        "ما اسمك": {
            "response_ar": "أنا ديب ماين، مساعدك الشخصي",
            "response_en": "My name is DeepMine, your personal assistant"
        }
    })
    
    test_cases = [
        "كم الساعة الآن؟",
        "ما اسمك؟",
        "هل تعرف الوقت الحالي؟",
        "ما هو اسمك الحقيقي؟"
    ]
    
    for test_input in test_cases:
        response = router.find_reply(test_input)
        print(f"الإدخال: '{test_input}' → الرد: {response}")

        