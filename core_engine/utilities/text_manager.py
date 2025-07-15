import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class TextManager:
    def __init__(self):
        """تهيئة مدير النصوص وتحميل ملفات البيانات"""
        self.base_dir = Path(__file__).parent.parent.parent
        self.welcome_msgs: Dict = {"time_based": {}, "event_based": {}}
        self.system_msgs: Dict = {"states": {}, "errors": {}}
        self.user_preferences: Dict = {
            "name_ar": "المستخدم",
            "name_en": "User",
            "birthdate": "2000-01-01",
            "preferences": {}
        }
        self.special_events: Dict = {"events": {}, "messages": {}}
        self.load_all_data()

      
        self.test_loaded_data()

    def load_all_data(self):
        """تحميل جميع ملفات البيانات"""
        self.load_welcome_messages()
        self.load_system_messages()
        self.load_user_preferences()
        self.load_special_events()

    def load_welcome_messages(self):
        try:
            with open(self.base_dir / "data/interaction/welcome_messages.json", encoding='utf-8') as f:
                self.welcome_msgs = json.load(f)
        except Exception as e:
            print(f"⚠️ خطأ في تحميل رسائل الترحيب: {e}")
            self.welcome_msgs = {"time_based": {}, "event_based": {}}

    def load_system_messages(self):
        try:
            with open(self.base_dir / "data/interaction/system_messages.json", encoding='utf-8') as f:
                self.system_msgs = json.load(f)
        except Exception as e:
            print(f"⚠️ خطأ في تحميل رسائل النظام: {e}")
            self.system_msgs = {"states": {}, "errors": {}}

    def load_user_preferences(self):
        try:
            with open(self.base_dir / "config/user_preferences.json", encoding='utf-8') as f:
                self.user_preferences.update(json.load(f))
        except Exception as e:
            print(f"⚠️ خطأ في تحميل ملف المستخدم: {e}")

    def load_special_events(self):
        try:
            with open(self.base_dir / "data/interaction/special_events.json", encoding='utf-8') as f:
                self.special_events = json.load(f)
        except Exception as e:
            print(f"⚠️ خطأ في تحميل الأحداث الخاصة: {e}")
            self.special_events = {"events": {}, "messages": {}}

    #------------------تنسيق الرسائل-حسب اللغة-----------------
    def format_message(self, text: str, lang: str = "ar") -> str:
        return text.format(
            name_ar=self.user_preferences.get("name_ar", "المستخدم"),
            name_en=self.user_preferences.get("name_en", "User")
        )

    def get_greeting(self, context: Optional[str] = None) -> Dict:
        hour = datetime.now().hour
        time_of_day = (
            "morning" if 5 <= hour < 12 else
            "afternoon" if 12 <= hour < 18 else
            "evening"
        )
        context = context or "time_based"
        msg_group = self.welcome_msgs.get(context, {}).get(
            time_of_day if context == "time_based" else context, {}
        )
        return {
            "text_ar": self.format_message(msg_group.get("ar", ""), "ar"),
            "text_en": self.format_message(msg_group.get("en", ""), "en"),
            "sound": msg_group.get("sound")
        }

    def get_system_msg(self, msg_type: str, lang: str = "ar") -> str:
        msg = self.system_msgs["states"].get(msg_type, {})
        return self.format_message(msg.get(lang, ""), lang)

    def get_error_msg(self, error_type: str, lang: str = "ar") -> str:
        msg = self.system_msgs["errors"].get(error_type, {})
        return self.format_message(msg.get(lang, ""), lang)

    def get_event_message(self, event_type: str, sub_key: Optional[str] = None, lang: str = "ar") -> str:
        messages = self.special_events["messages"].get(event_type, {})
        if sub_key and isinstance(messages, dict):
            messages = messages.get(sub_key, {})
        return self.format_message(messages.get(lang, "") if isinstance(messages, dict) else messages, lang)

    def check_special_events(self, lang: str = "ar") -> Optional[str]:
        today = datetime.now().date()
        try:
            birthday = datetime.strptime(self.user_preferences["birthdate"], "%Y-%m-%d").date()
            bday_this_year = birthday.replace(year=today.year)
            delta = (bday_this_year - today).days
            if delta in (10, 3, 1, 0):
                key = f"{delta}_days" if delta > 1 else "today" if delta == 0 else "1_day"
                return self.get_event_message("birthday_countdown", key, lang)
        except Exception as e:
            print(f"⚠️ خطأ في معالجة عيد الميلاد: {e}")

        for event, date_str in self.special_events["events"].items():
            try:
                if datetime.strptime(date_str, "%Y-%m-%d").date() == today:
                    return self.get_event_message(event, lang=lang)
            except Exception as e:
                print(f"⚠️ خطأ في معالجة مناسبة {event}: {e}")
        return None

    def get_user_name(self, lang: str = "ar") -> str:
        return self.user_preferences.get(f"name_{lang}", "")

    def get_full_preferences(self) -> Dict:
        return self.user_preferences

    def save_user_preferences(self):
        try:
            with open(self.base_dir / "config/user_preferences.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ ملف المستخدم: {e}")


    def test_loaded_data(self):
        print("\n✅ نتائج التحقق من تحميل الملفات:\n")
    
        print("📦 welcome_messages:", "✅ تم التحميل" if self.welcome_msgs["time_based"] else "❌ فارغ")
        print("📦 system_messages:", "✅ تم التحميل" if self.system_msgs["states"] else "❌ فارغ")
        print("📦 user_preferences:", "✅ تم التحميل" if self.user_preferences else "❌ فارغ")
        print("📦 special_events:", "✅ تم التحميل" if self.special_events["events"] else "❌ فارغ")        