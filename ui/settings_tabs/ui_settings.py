# ui/settings_tabs/ui_settings.py
# وصف هذا الملف واجهة إعدادات المستخدم التي تحتوي على علامات تبويب مختلفة لضبط إعدادات الواجهة مثل الرؤية والسلوك.
# يتم استخدام PyQt5 لإنشاء واجهة المستخدم الرسومية. 

# واجهة إعدادات المستخدم: تبويبات الرؤية والسلوك والثيم ومكونات الواجهة


import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QFormLayout, QGroupBox, QColorDialog,
    QPushButton, QFontComboBox, QSpinBox, QCheckBox, QHBoxLayout, QFileDialog, QMessageBox
)
from .visibility_tab import VisibilityTab
from .behavior_tab import BehaviorTab

class ThemeTab(QWidget):
    def __init__(self, theme_settings, parent=None):
        super().__init__(parent)
        self.theme_settings = self.convert_theme_settings(theme_settings)
        layout = QFormLayout(self)

        # اللون الأساسي
        self.color_lbl = QLabel(self.theme_settings.get("primary_color", "#4e9de6"))
        color_btn = QPushButton("اختر اللون الأساسي")
        color_btn.clicked.connect(self.choose_color)

        # الوضع الداكن
        self.dark_mode_chk = QCheckBox("تفعيل الوضع الداكن")
        self.dark_mode_chk.setChecked(self.theme_settings.get("dark_mode", True))

        # الخط
        font_group = QGroupBox("الخط")
        font_layout = QHBoxLayout()
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentText(self.theme_settings.get("font", {}).get("family", "Arial"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 48)
        self.font_size.setValue(self.theme_settings.get("font", {}).get("size", 14))
        self.font_bold = QCheckBox("عريض")
        self.font_bold.setChecked(self.theme_settings.get("font", {}).get("bold", False))
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(self.font_size)
        font_layout.addWidget(self.font_bold)
        font_group.setLayout(font_layout)

        layout.addRow("اللون الأساسي:", color_btn)
        layout.addRow("القيمة الحالية:", self.color_lbl)
        layout.addRow(self.dark_mode_chk)
        layout.addRow(font_group)

    def convert_theme_settings(self, settings):
        """تحويل إعدادات الثيم إلى قاموس"""
        if isinstance(settings, set):
            return {
                "primary_color": "#4e9de6",
                "dark_mode": True,
                "font": {"family": "Arial", "size": 14, "bold": False}
            }
        return settings
        
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_lbl.setText(color.name())

    def get_settings(self):
        return {
            "primary_color": self.color_lbl.text(),
            "dark_mode": self.dark_mode_chk.isChecked(),
            "font": {
                "family": self.font_combo.currentText(),
                "size": self.font_size.value(),
                "bold": self.font_bold.isChecked()
            }
        }

class ElementsTab(QWidget):
    def __init__(self, elements_settings, parent=None):
        super().__init__(parent)
        self.elements_settings = elements_settings
        layout = QFormLayout(self)

        # صندوق النص
        text_box = self.elements_settings.get("text_box", {})
        self.text_visible = QCheckBox("إظهار صندوق النص")
        self.text_visible.setChecked(text_box.get("visible", True))
        self.text_editable = QCheckBox("قابل للتحرير")
        self.text_editable.setChecked(text_box.get("editable", True))
        self.text_placeholder = QLabel(f"النص الافتراضي: {text_box.get('placeholder', 'اكتب هنا...')}")

        # زر المايك
        mic_button = self.elements_settings.get("mic_button", {})
        self.mic_visible = QCheckBox("إظهار زر المايك")
        self.mic_visible.setChecked(mic_button.get("visible", True))
        self.mic_position = QLabel(f"الموضع: {mic_button.get('position', [1200, 300])}")

        layout.addRow(self.text_visible)
        layout.addRow(self.text_editable)
        layout.addRow(self.text_placeholder)
        layout.addRow(self.mic_visible)
        layout.addRow(self.mic_position)

    def get_settings(self):
        return {
            "text_box": {
                "visible": self.text_visible.isChecked(),
                "editable": self.text_editable.isChecked(),
                "placeholder": self.text_placeholder.text().replace("النص الافتراضي: ", "")
            },
            "mic_button": {
                "visible": self.mic_visible.isChecked(),
                "position": eval(self.mic_position.text().replace("الموضع: ", ""))
            }
        }

class UISettingsTab(QWidget):
    def __init__(self, ui_settings, parent=None):
        super().__init__(parent)
        self.ui_settings = self.convert_ui_settings(ui_settings)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # تبويب الرؤية
        self.visibility_tab = VisibilityTab(self.ui_settings.get('elements', {}))
        self.tabs.addTab(self.visibility_tab, "👁️ الرؤية")

        # تبويب السلوك
        self.behavior_tab = BehaviorTab(self.ui_settings.get('behavior', {}))
        self.tabs.addTab(self.behavior_tab, "🚀 السلوك")

        # تبويب الثيم
        self.theme_tab = ThemeTab(self.ui_settings.get('theme', {}))
        self.tabs.addTab(self.theme_tab, "🎨 الثيم")

        # تبويب مكونات الواجهة
        self.elements_tab = ElementsTab(self.ui_settings.get('elements', {}))
        self.tabs.addTab(self.elements_tab, "🧩 المكونات")

        layout.addWidget(self.tabs)

        # أزرار الحفظ ورفع ملف افتراضي
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 حفظ التعديلات")
        save_btn.clicked.connect(self.save_settings)
        load_btn = QPushButton("⬆️ رفع ملف إعدادات افتراضي")
        load_btn.clicked.connect(lambda: QFileDialog.getOpenFileName(self, "رفع ملف إعدادات افتراضي", "", "JSON Files (*.json)"))
        load_btn.setEnabled(False)  # يمكن تفعيل هذا الزر لاحقًا حسب الحاجة
        # زر إعادة تعيين الإعدادات الافتراضية   
        reset_btn = QPushButton("🔄 استعادة الإعدادات الافتراضية")
        reset_btn.clicked.connect(self.reset_to_defaults)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)

    def convert_ui_settings(self, settings):
        """تحويل إعدادات الواجهة إلى الشكل الصحيح"""
        if isinstance(settings, set):
            # تحويل المجموعة إلى قاموس بالقيم الافتراضية
            return {
                "theme": {
                    "primary_color": "#4e9de6",
                    "dark_mode": True,
                    "font": {"family": "Arial", "size": 14, "bold": False}
                },
                "behavior": {
                    "inactivity_timeout": 5,
                    "animation_speed": "medium",
                    "shrink_settings": {"enabled": True, "duration": 0.5, "hide_after": True}
                },
                "elements": {
                    "text_box": {"visible": True, "editable": True, "placeholder": "اكتب هنا..."},
                    "mic_button": {"visible": True, "position": [1200, 300]}
                }
            }
        return settings

    def save_settings(self):
        # جمع الإعدادات من كل تبويب
        new_settings = {
            "theme": self.theme_tab.get_settings(),
            "behavior": self.behavior_tab.get_settings() if hasattr(self.behavior_tab, "get_settings") else self.ui_settings.get("behavior", {}),
            "elements": self.elements_tab.get_settings()
        }
        # تحديث ملف الإعدادات
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ui_settings.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_settings, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "تم الحفظ", "تم حفظ إعدادات الواجهة بنجاح.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الحفظ", f"تعذر حفظ الإعدادات:\n{e}")



    def reset_to_defaults(self):
        default_settings = {
            "theme": {
                "primary_color": "#4e9de6",
                "dark_mode": True,
                "font": {"family": "Arial", "size": 14, "bold": False}
            },
            "behavior": {
                "inactivity_timeout": 5,
                "animation_speed": "medium",
                "shrink_settings": {"enabled": True, "duration": 0.5, "hide_after": True}
            },
            "elements": {
                "text_box": {"visible": True, "editable": True, "placeholder": "اكتب هنا..."},
                "mic_button": {"visible": True, "position": [1200, 300]}
            }
        }
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ui_settings.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "تم الاستعادة", "تمت استعادة الإعدادات الافتراضية بنجاح.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاستعادة:\n{e}")

    @staticmethod
    def load_settings():
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ui_settings.json"
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # إضافة الأقسام المفقودة بالقيم الافتراضية
                    defaults = {
                        "theme": { ... },
                        "behavior": { ... },
                        "elements": { ... },
                        "text": {
                            "editable": True,
                            "placeholder": "اكتب هنا...",
                            "font_family": "Arial",
                            "font_size": 12,
                            "text_color": "#FFFFFF",
                            "display_mode": "فوري",
                            "display_speed": 50,
                            "fade_out_before_shrink": True
                        },
                        "audio_ui": {
                            "voice_gender": "أنثوي",
                            "voice_language": "العربية",
                            "voice_quality": "عالية",
                            "audio_output_device": "افتراضي",
                            "save_user_voice": False,
                            "user_voice_path": "/path/to/save",
                            "mic_interaction_mode": "اضغط للتحدث"
                        }
                    }
                    
                    # دمج الإعدادات مع القيم الافتراضية
                    for key in defaults:
                        if key not in data:
                            data[key] = defaults[key]
                    
                    return {'ui': data}
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
        
        # العودة إلى القيم الافتراضية الكاملة
        return {
            "ui": {
                "theme": { ... },
                "behavior": { ... },
                "elements": { ... },
                "text": { ... },
                "audio_ui": { ... }
            }
        }