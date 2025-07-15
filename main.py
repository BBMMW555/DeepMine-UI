import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import json
import os

from core_engine.command_processing.command_handler import CommandHandler
from core_engine.speech_processing.speech_manager import SpeechManager
from core_engine.utilities.logger import setup_logger
from core_engine.utilities.file_utils import load_json, save_json
from ui.main_window import MainWindow
from ui.uisettings_manager import uisettingsmanager
from core_engine.context_manager import ContextManager
from core_engine.utilities.settings_manager import SettingsManager
from watchdog.observers import Observer


# تحميل الإعدادات من config.json (6- config.json)
def load_config():
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        # إعدادات افتراضية في حال عدم وجود الملف
        default_config = {
            "first_run": True,
            "system": {"version": "1.0.0"},
            "paths": {
                "models": "models",
                "logs": "logs"
            },
            "config_files": {
                "audio": "config/audio_settings.json",
                "system": "config/system_config.json",
                "ui": "config/ui_settings.json",
                "user": "config/user_preferences.json",
                "voice_frequencies": "config/voice_frequencies.json",
                "wake_word": "config/wake_word_settings.json"
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في تحميل الإعدادات: {e}")
        return {}

def save_config(config):
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def first_run_setup():
    # إنشاء ملفات افتراضية إذا لم تكن موجودة
    default_files = {
        'data/keywords.json': {"keywords": []},
        'data/learned_actions.json': {"actions": []}
    }
    for rel_path, content in default_files.items():
        abs_path = Path(__file__).parent / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        if not abs_path.exists():
            with open(abs_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)

def main():
    # 1. تحميل الإعدادات العامة
    config = load_config()
    settings_manager = SettingsManager("config.json")
    

    # 2. الحصول على مسارات مهمة
    models_path = settings_manager.get_path("models")
    logs_path = settings_manager.get_path("logs")
    print(f"📁 مسار النماذج: {models_path}")
    print(f"📁 مسار السجلات: {logs_path}")

    # 3. الوصول للإعدادات المختلفة
    system_version = settings_manager.get("system", "version", "1.0.0")
    ui_color = settings_manager.get("ui", "theme/primary_color", "#4e9de6")
    print(f"⚙️ إصدار النظام: {system_version}")
    print(f"🎨 لون الواجهة: {ui_color}")

    # 4. تهيئة نظام التسجيل
    setup_logger()

    # 5. تهيئة أولية إذا لزم الأمر
    if config.get("first_run", True):
        first_run_setup()
        config["first_run"] = False
        save_config(config)

    # 6. تهيئة التطبيق
    app = QApplication(sys.argv)

    try:
        # 7. تهيئة مدير السياق
        max_context = settings_manager.get("system", "max_context", 5)
        context_manager = ContextManager(max_context=max_context)

        # 8. تهيئة مدير الكلام
        base_dir = Path(__file__).resolve().parent
        model_path = base_dir / "models" / "vosk-model-ar-0.22-linto-1.1.0"
        if not model_path.exists():
            print(f"❌ نموذج الصوت غير موجود في: {model_path}")

        speech_manager = SpeechManager(model_path=str(model_path))

        # 9. تهيئة معالج الأوامر
        command_handler = CommandHandler(context_manager=context_manager)

        # 10. إنشاء الواجهة الرئيسية
        window = MainWindow(
            speech_manager=speech_manager,
            command_handler=command_handler,
            context_manager=context_manager,
            uisettings_manager=uisettingsmanager(),
            settings_manager=settings_manager
        )
        
             

        # 11. بدء التطبيق
        if settings_manager.get("system", "auto_start", True):
            def handle_command(command):
                response = command_handler.handle(command)
                if 'data' in response and 'message' in response['data']:
                    main_window.display_bilingual_message({
                        'text_ar': response['data']['message'],
                        'text_en': response['data']['message']
                    })
                else:
                    main_window.display_bilingual_message({
                        'text_ar': "تم تنفيذ الأمر",
                        'text_en': "Command executed"
                    })
            speech_manager.start_listening(handle_command)

        main_window.show()
        sys.exit(app.exec_())

    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()