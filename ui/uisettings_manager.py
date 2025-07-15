import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QDateEdit, QPushButton, QMessageBox, QFormLayout,
                            QGroupBox, QListWidget, QStackedWidget, QWidget,
                            QComboBox, QCheckBox, QSlider, QRadioButton,
                             QButtonGroup,QTabWidget, QFontComboBox, QColorDialog,

                            QFrame, QSizePolicy, QSpacerItem, QFileDialog)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
import json

import getpass
import os
import platform
import traceback

from datetime import datetime
from hijri_converter import convert
import wave
import pyaudio
import time

from PyQt5.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve,QDate, Qt, QSize



# ... (الاستيرادات الحالية)
from ui.settings_tabs.visibility_tab import VisibilityTab # 1
from ui.settings_tabs.behavior_tab import BehaviorTab # 2
from ui.settings_tabs.text_tab import TextTab # 3
from ui.settings_tabs.audio_tab import AudioTab # 4
from ui.settings_tabs.extra_tab import ExtraTab # 5
from ui.settings_tabs.wake_word import WakeWordTab
from ui.settings_tabs.ui_settings import UISettingsTab # 6


class uisettingsmanager(QDialog):
    def __init__(self, parent=None, first_run=False):
        super().__init__(parent)
        self.first_run = first_run
        self.settings = self.fix_settings(UISettingsTab.load_settings())
        self.settings = UISettingsTab.load_settings()
        self.setWindowTitle("الإعدادات المتقدمة - DeepMine" if not first_run else "مرحبًا بك في DeepMine")
        self.setMinimumSize(1000, 700) if not first_run else self.setMinimumSize(900, 600)
        self.setStyleSheet(self.get_stylesheet(first_run))
        
        # تحميل البيانات الحالية
        self.profile_path = self.get_profile_path()
        self.current_profile = self.load_profile()
        
        # إنشاء عناصر الواجهة
        self.setup_ui(first_run)
        
        # إذا كانت شاشة الترحيب الأولى
        if first_run:
            self.setup_welcome_page()

        self.text_tab = None
        self.audio_tab = None
        self.extra_tab = None    
        
    def fix_settings(self, settings):
        """إصلاح هيكل الإعدادات"""
        if 'ui' not in settings:
            return {'ui': settings}
        return settings
        
    def get_profile_path(self):
        """الحصول على مسار ملف المستخدم"""
        project_path = Path(__file__).resolve().parent.parent.parent
        return project_path / "config" / "user_preferences.json"
    
    

    @staticmethod
    def load_settings():
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ui_settings.json"
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # ... باقي الكود ...
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
        # ... القيم الافتراضية ...

    def get_stylesheet(self, is_welcome=False):
        """إرجاع أنماط CSS للواجهة"""
        if is_welcome:
            return """
                QDialog {
                    background-color: #1a1a2e;
                    background-image: radial-gradient(circle at center, #16213e 0%, #0f3460 100%);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #e6e6e6;
                }
                QLabel {
                    color: #e6e6e6;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #4e9de6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 25px;
                    font-size: 16px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #3d7bc8;
                }
                QPushButton:pressed {
                    background-color: #2a5a9c;
                }
                QLineEdit, QComboBox, QDateEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #e6e6e6;
                    border: 1px solid #4e9de6;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QGroupBox {
                    background-color: rgba(30, 30, 46, 0.7);
                    color: #4e9de6;
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #4e9de6;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 15px;
                }
                QRadioButton {
                    color: #e6e6e6;
                    font-size: 14px;
                    spacing: 8px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    border: 2px solid #4e9de6;
                }
                QRadioButton::indicator:checked {
                    background-color: #4e9de6;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #4e9de6;
                    height: 8px;
                    background: rgba(30, 30, 46, 0.7);
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #4e9de6;
                    border: 1px solid #2a5a9c;
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    margin: -6px 0;
                }
            """
        else:
            return """
                QDialog {
                    background-color: #1a1a2e;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                QGroupBox {
                    background-color: rgba(30, 30, 46, 0.7);
                    color: #4e9de6;
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #4e9de6;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 15px;
                }
                QLabel {
                    color: #e6e6e6;
                    font-size: 14px;
                }
                QLineEdit, QDateEdit, QComboBox, QListWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #e6e6e6;
                    border: 1px solid #4e9de6;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #4e9de6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #3d7bc8;
                }
                QPushButton:pressed {
                    background-color: #2a5a9c;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #4e9de6;
                    height: 8px;
                    background: rgba(30, 30, 46, 0.7);
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #4e9de6;
                    border: 1px solid #2a5a9c;
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    margin: -6px 0;
                }
                QRadioButton {
                    color: #e6e6e6;
                    font-size: 14px;
                    spacing: 8px;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    border: 2px solid #4e9de6;
                }
                QRadioButton::indicator:checked {
                    background-color: #4e9de6;
                }
            """
    
    def setup_ui(self, is_welcome=False):
        """تهيئة واجهة المستخدم"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # شاشة الترحيب الأولى
        if is_welcome:
            self.setup_welcome_page()
            return
        
        # شريط التبويبات الجانبي
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(10)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 30, 46, 0.7);
                border: 1px solid #4e9de6;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidget::item {
                color: #e6e6e6;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #4e9de6;
                color: white;
            }
        """)
        
        # تبويبات الإعدادات الجديدة
        tabs = [
            {"icon": "👤", "title": "الملف الشخصي"},
            {"icon": "💻", "title": "التفاعل والواجهة"},
            {"icon": "✏️", "title": "إعدادات النص"},  
            {"icon": "🎧", "title": "إعدادات الصوت"},  
            {"icon": "🎙️", "title": "الاستدعاء والاستماع"},
            {"icon": "⚡", "title": "التخصيصات الذكية"},
            {"icon": "⚙️", "title": "إضافات"},
            {"icon": "ℹ️", "title": "حول التطبيق"}
        ]
        
        for tab in tabs:
            self.sidebar.addItem(f"{tab['icon']} {tab['title']}")
        
        # منطقة المحتوى
        self.content_stack = QStackedWidget()
        
        # إنشاء التبويبات
        self.create_profile_tab()
        
       
        self.create_text_tab()     
        self.create_audio_tab()    
        self.create_smart_tab()
        self.create_extra_tab()    
        self.create_about_tab()

        ui_tab = UISettingsTab(self.settings['ui'])
        self.content_stack.addWidget(ui_tab)

        # ربط تغيير التبويب
        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        
        # إضافة العناصر
        tab_layout.addWidget(self.sidebar)
        tab_layout.addWidget(self.content_stack, 1)
        
        # خط فاصل
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #4e9de6; height: 1px;")
        
        # زر الحفظ والإغلاق
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("💾 حفظ الإعدادات")
        save_btn.setIcon(QIcon("assets/icons/save.png"))
        save_btn.clicked.connect(self.save_settings)
        
        close_btn = QPushButton("❌ إغلاق" if not self.first_run else "🚀 بدء الاستخدام")
        close_btn.setIcon(QIcon("assets/icons/close.png"))
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(close_btn)
        
        # التخطيط الرئيسي
        main_layout.addLayout(tab_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        # تحديد التبويب الأول
        self.sidebar.setCurrentRow(0)

    def setup_welcome_page(self):
        """تهيئة صفحة الترحيب الأولى"""
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # العنوان
        title = QLabel("🎉 مرحبًا بك في مساعدك الشخصي DeepMine")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4e9de6;")
        title.setAlignment(Qt.AlignCenter)
        
        # الرسالة الترحيبية
        message = QLabel(
            "نحن هنا لتقديم تجربة صوتية سلسة وذكية. يمكنك أن تطلب مني كتابة الملاحظات، فتح الإعدادات، "
            "تذكيرك بالأحداث، أو حتى الدردشة معي.\n\n"
            "لنبدأ بإعداداتك الأساسية:"
        )
        message.setStyleSheet("font-size: 16px; color: #e6e6e6;")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        
        # إعدادات اللغة
        lang_layout = QHBoxLayout()
        lang_label = QLabel("🌐 اختيار اللغة:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English", "Français", "Español"])
        self.lang_combo.setCurrentText("العربية")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        # إعدادات المظهر
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 اختيار المظهر:")
        
        self.theme_group = QButtonGroup(self)
        self.light_theme = QRadioButton("فاتح")
        self.dark_theme = QRadioButton("داكن")
        self.dark_theme.setChecked(True)
        
        self.theme_group.addButton(self.light_theme)
        self.theme_group.addButton(self.dark_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.light_theme)
        theme_layout.addWidget(self.dark_theme)
        theme_layout.addStretch()
        
        # تفعيل التوجيه الصوتي
        self.voice_guide_check = QCheckBox("🔔 تفعيل التوجيه الصوتي (إرشادات الاستخدام)")
        self.voice_guide_check.setChecked(True)
        
        # زر معرفة قدرات التطبيق
        features_btn = QPushButton("🧠 اعرف قدرات التطبيق")
        features_btn.setStyleSheet("background-color: #8a4eb8; font-size: 16px; padding: 12px;")
        features_btn.clicked.connect(self.show_features)
        
        # زر المتابعة
        next_btn = QPushButton("التالي ➡️")
        next_btn.setStyleSheet("font-size: 18px; padding: 15px 30px;")
        next_btn.clicked.connect(self.show_user_setup)
        
        # إضافة العناصر
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addLayout(lang_layout)
        layout.addLayout(theme_layout)
        layout.addWidget(self.voice_guide_check)
        layout.addWidget(features_btn)
        layout.addStretch()
        layout.addWidget(next_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def show_features(self):
        """عرض قدرات التطبيق للمستخدم"""
        features = (
            "🌟 قدرات مساعد DeepMine:\n\n"
            "• كتابة الملاحظات والرسائل بالصوت\n"
            "• البحث في الإنترنت والملفات\n"
            "• إدارة التقويم والمواعيد\n"
            "• قراءة البريد الإلكتروني\n"
            "• التحكم في الجهاز (فتح التطبيقات، ضبط الصوت، إلخ)\n"
            "• الإجابة على الأسئلة المعرفية\n"
            "• تحويل الصوت إلى نص والعكس\n"
            "• تذكيرات ذكية بناءً على العادات\n"
            "• الدردشة التفاعلية الذكية"
        )
        
        QMessageBox.information(
            self,
            "قدرات التطبيق",
            features,
            QMessageBox.Ok
        )
    
    def show_user_setup(self):
        """عرض شاشة إعداد المستخدم"""
        # حذف التخطيط الحالي
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # العنوان
        title = QLabel("👤 إعدادات المستخدم الشخصية")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4e9de6;")
        title.setAlignment(Qt.AlignCenter)
        
        # الاسم
        name_layout = QHBoxLayout()
        name_label = QLabel("اسم المستخدم:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ما الاسم الذي تحب أن أناديك به؟")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        # تسجيل الصوت
        voice_group = QGroupBox("🎙️ تسجيل بصمة صوتية")
        voice_layout = QVBoxLayout()
        
        voice_instruction = QLabel("سجل عبارة مثل \"أنا مستعد\" لإنشاء بصمة صوتية خاصة بك:")
        self.record_btn = QPushButton("⏺️ بدء التسجيل")
        self.record_btn.setStyleSheet("background-color: #e74c3c; font-size: 16px; padding: 12px;")
        self.record_btn.clicked.connect(self.toggle_recording)
        
        self.record_status = QLabel("الحالة: غير مسجل")
        self.record_status.setStyleSheet("color: #e6e6e6; font-size: 14px;")
        
        voice_layout.addWidget(voice_instruction)
        voice_layout.addWidget(self.record_btn)
        voice_layout.addWidget(self.record_status)
        voice_group.setLayout(voice_layout)
        
        # زر الإنهاء
        finish_btn = QPushButton("✅ تم الإعداد")
        finish_btn.setStyleSheet("font-size: 18px; padding: 15px 30px;")
        finish_btn.clicked.connect(self.finish_setup)
        
        # إضافة العناصر
        layout.addWidget(title)
        layout.addLayout(name_layout)
        layout.addWidget(voice_group)
        layout.addStretch()
        layout.addWidget(finish_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    def create_text_tab(self):
        """إنشاء تبويب إعدادات النص"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_tab = TextTab(self.settings['ui'].get('text', {}))
        layout.addWidget(self.text_tab)
        
        self.content_stack.addWidget(tab)
     

    def create_audio_tab(self):
        """إنشاء تبويب إعدادات الصوت"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.audio_tab = AudioTab(self.settings['ui']['audio_ui'])
        layout.addWidget(self.audio_tab)
        
        self.content_stack.addWidget(tab)

    def create_extra_tab(self):
        """إنشاء تبويب الإضافات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.extra_tab = ExtraTab(self.settings['ui'].get('extra', {}))
        layout.addWidget(self.extra_tab)
        
        self.content_stack.addWidget(tab)    
    
    def toggle_recording(self):
        """تبديل حالة التسجيل الصوتي"""
        if not hasattr(self, 'is_recording'):
            self.is_recording = False
        
        if not self.is_recording:
            self.start_recording()
            self.record_btn.setText("⏹️ إيقاف التسجيل")
            self.record_btn.setStyleSheet("background-color: #2ecc71; font-size: 16px; padding: 12px;")
            self.record_status.setText("الحالة: جاري التسجيل...")
        else:
            self.stop_recording()
            self.record_btn.setText("⏺️ بدء التسجيل")
            self.record_btn.setStyleSheet("background-color: #e74c3c; font-size: 16px; padding: 12px;")
            self.record_status.setText("الحالة: تم التسجيل بنجاح")
        
        self.is_recording = not self.is_recording
    
    def start_recording(self):
        """بدء تسجيل الصوت"""
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  input=True,
                                  frames_per_buffer=1024,
                                  stream_callback=self.record_callback)
        self.stream.start_stream()
    
    def record_callback(self, in_data, frame_count, time_info, status):
        """دالة رد الاتصال للتسجيل"""
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_recording(self):
        """إيقاف تسجيل الصوت وحفظه"""
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
        # حفظ التسجيل
        voice_path = Path(__file__).resolve().parent.parent.parent / "DeepMine" / "data" / "voiceprint.wav"
        wf = wave.open(str(voice_path), 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
    
    def finish_setup(self):
        """إنهاء عملية الإعداد"""
        # حفظ الإعدادات
        self.save_initial_settings()
        self.accept()
    
    def save_initial_settings(self):
        """حفظ الإعدادات الأولية"""
        config_path = Path(__file__).resolve().parent.parent.parent / "DeepMine" / "config" / "ui_settings.json"
        
        config = {
            "first_run": False,
            "language": "ar",
            "theme": "dark" if self.dark_theme.isChecked() else "light",
            "voice_guide": self.voice_guide_check.isChecked(),
            "user_name": self.name_input.text().strip() or "المستخدم"
        }
        
        # إنشاء المجلدات إذا لم تكن موجودة
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def create_profile_tab(self):
        """إنشاء تبويب الملف الشخصي"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        group = QGroupBox("👤 المعلومات الشخصية")
        form = QFormLayout()
        form.setSpacing(15)
        
        # الاسم العربي
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setText(self.current_profile.get("name_ar", ""))
        form.addRow("الاسم العربي:", self.name_ar_input)
        
        # الاسم الإنجليزي
        self.name_en_input = QLineEdit()
        self.name_en_input.setText(self.current_profile.get("name_en", ""))
        form.addRow("الاسم الإنجليزي:", self.name_en_input)
        
        # تاريخ الميلاد
        birth_container = QHBoxLayout()
        self.gregorian_input = QDateEdit()
        self.gregorian_input.setCalendarPopup(True)
        self.gregorian_input.setDisplayFormat("yyyy-MM-dd")
        self.gregorian_input.dateChanged.connect(self.convert_to_hijri)
        birth_container.addWidget(QLabel("الميلادي:"))
        birth_container.addWidget(self.gregorian_input)
        
        self.hijri_input = QLineEdit()
        self.hijri_input.setPlaceholderText("YYYY-MM-DD")
        self.hijri_input.textChanged.connect(self.convert_to_gregorian)
        birth_container.addWidget(QLabel("الهجري:"))
        birth_container.addWidget(self.hijri_input)
        
        form.addRow("تاريخ الميلاد:", birth_container)
        self.load_birthdate()
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        
        self.content_stack.addWidget(tab)
    
    def load_birthdate(self):
        """تحميل تاريخ الميلاد في الحقول المناسبة"""
        try:
            birthdate_str = self.current_profile.get("birthdate", "2000-01-01")
            if not isinstance(birthdate_str, str):
                birthdate_str = "2000-01-01" 
            
            # تحويل التاريخ إلى الصيغة اللاتينية
            latin_date = self.convert_date_to_latin(birthdate_str)
            
            # تحميل التاريخ الميلادي
            birthdate = QDate.fromString(latin_date, "yyyy-MM-dd")
            if birthdate.isValid():
                self.gregorian_input.setDate(birthdate)
                
                # تحويل إلى هجري وعرضه
                hijri_date = self.gregorian_to_hijri(latin_date)
                self.hijri_input.setText(hijri_date)
            else:
                # إذا كان التاريخ غير صالح، استخدم القيمة الافتراضية
                self.gregorian_input.setDate(QDate(2000, 1, 1))
                self.hijri_input.setText("1420-10-21")
                print(f"⚠️ تاريخ الميلاد غير صالح: {birthdate_str}")
            
        except Exception as e:
            print(f"خطأ في تحميل تاريخ الميلاد: {e}")
            self.gregorian_input.setDate(QDate(2000, 1, 1))
            self.hijri_input.setText("1420-10-21")
    
    def convert_date_to_latin(self, date_str: str) -> str:
        """تحويل تاريخ من الصيغة العربية إلى اللاتينية"""
        # قاموس تحويل الأرقام العربية إلى لاتينية
        digit_map = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
        }
        
        # تحويل كل حرف في التاريخ
        latin_date = ''.join(digit_map.get(char, char) for char in date_str)
        return latin_date
    
    def gregorian_to_hijri(self, date_str: str) -> str:
        """تحويل التاريخ الميلادي إلى هجري"""
        try:
            # تقسيم التاريخ إلى أجزاء
            year, month, day = map(int, date_str.split('-'))
            
            # التحويل باستخدام المكتبة
            hijri = convert.Gregorian(year, month, day).to_hijri()
            return f"{hijri.year}-{hijri.month:02d}-{hijri.day:02d}"
        except Exception as e:
            print(f"⚠️ خطأ في تحويل التاريخ: {e}")
            return date_str
    
    def hijri_to_gregorian(self, date_str: str) -> str:
        """تحويل التاريخ الهجري إلى ميلادي"""
        try:
            # تحويل التاريخ إلى الصيغة اللاتينية
            latin_date = self.convert_date_to_latin(date_str)
            
            # تقسيم التاريخ
            year, month, day = map(int, latin_date.split('-'))
            
            # التحويل باستخدام المكتبة
            gregorian = convert.Hijri(year, month, day).to_gregorian()
            return f"{gregorian.year}-{gregorian.month:02d}-{gregorian.day:02d}"
        except Exception as e:
            print(f"⚠️ خطأ في تحويل التاريخ: {e}")
            return date_str
    
    def convert_to_hijri(self):
        """تحويل التاريخ الميلادي إلى هجري وعرضه"""
        try:
            gregorian_date = self.gregorian_input.date().toString("yyyy-MM-dd")
            hijri_date = self.gregorian_to_hijri(gregorian_date)
            self.hijri_input.setText(hijri_date)
        except Exception as e:
            print(f"خطأ في التحويل إلى الهجري: {e}")
    
    def convert_to_gregorian(self):
        """تحويل التاريخ الهجري إلى ميلادي وعرضه"""
        try:
            hijri_date = self.hijri_input.text().strip()
            if hijri_date and len(hijri_date) == 10 and hijri_date[4] == '-' and hijri_date[7] == '-':
                gregorian_date = self.hijri_to_gregorian(hijri_date)
                date_obj = QDate.fromString(gregorian_date, "yyyy-MM-dd")
                if date_obj.isValid():
                    self.gregorian_input.setDate(date_obj)
                else:
                    print(f"⚠️ التاريخ الميلادي غير صالح: {gregorian_date}")
        except Exception as e:
            print(f"خطأ في التحويل إلى الميلادي: {e}")
    

    def create_smart_tab(self):
        """إنشاء تبويب التخصيصات الذكية"""
       
        tab = WakeWordTab()
        self.content_stack.addWidget(tab)
    
    
    def create_about_tab(self):
        """إنشاء تبويب حول التطبيق"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # شعار التطبيق
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/icons/logo.png").scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # معلومات التطبيق
        name_label = QLabel("DeepMine - المساعد الذكي")
        name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4e9de6;")
        name_label.setAlignment(Qt.AlignCenter)
        
        version_label = QLabel("الإصدار: 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        
        model_label = QLabel("نموذج الصوت: vosk-model-ar-0.22-linto-1.1.0")
        model_label.setAlignment(Qt.AlignCenter)
        
        # مميزات التطبيق
        features_group = QGroupBox("🌟 مميزات المساعد")
        features_layout = QVBoxLayout()
        
        features = [
            "تحويل الصوت إلى نص بدقة عالية",
            "التعرف على الأوامر الصوتية المخصصة",
            "كتابة الملاحظات والوثائق بالصوت",
            "التفاعل الذكي مع الأوامر المعقدة",
            "دعم متعدد اللغات (قريبًا)",
            "تخصيص كامل لتجربة المستخدم"
        ]
        
        for feature in features:
            feature_label = QLabel(f"• {feature}")
            features_layout.addWidget(feature_label)
        
        features_group.setLayout(features_layout)
        
        # الدعم والملاحظات
        support_label = QLabel("📧 للدعم أو الإبلاغ عن مشاكل: support@deepmine.com")
        support_label.setAlignment(Qt.AlignCenter)
        
        feedback_btn = QPushButton("✏️ إرسال ملاحظات")
        feedback_btn.setStyleSheet("background-color: #8a4eb8;")
        feedback_btn.clicked.connect(self.send_feedback)
        
        # إضافة العناصر
        layout.addWidget(logo_label)
        layout.addWidget(name_label)
        layout.addWidget(version_label)
        layout.addWidget(model_label)
        layout.addSpacing(20)
        layout.addWidget(features_group)
        layout.addSpacing(20)
        layout.addWidget(support_label)
        layout.addWidget(feedback_btn)
        layout.addStretch()
        
        self.content_stack.addWidget(tab)
    
    def send_feedback(self):
        """فتح نافذة لإرسال الملاحظات"""
        QMessageBox.information(
            self,
            "إرسال ملاحظات",
            "يمكنك إرسال ملاحظاتك على البريد الإلكتروني: support@deepmine.com\n\n"
            "سنكون سعداء بسماع آرائك ومقترحاتك لتحسين التطبيق!",
            QMessageBox.Ok
        )
    
    def load_profile(self):
        """تحميل بيانات المستخدم الحالية"""
        try:
            if self.profile_path.exists():
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
        
        # العودة إلى القيم الافتراضية
        return {
            "name_ar": "المستخدم",
            "name_en": self.get_system_username(),
            "birthdate": "2000-01-01",
            "preferences": {
                "voice_gender": "female",
                "greeting_style": "ودود",
                "auto_greeting": True,
                "enable_event_notifications": True
            }
        }
    
    def get_system_username(self):
        """الحصول على اسم مستخدم النظام"""
        try:
            return getpass.getuser()
        except:
            return "User"
    
    
    def save_settings(self):
        """حفظ الإعدادات الجديدة"""
        try:
            # تحديث إعدادات التبويبات إذا كانت موجودة
            if hasattr(self, 'visibility_tab') and self.visibility_tab:
                self.visibility_tab.update_settings()
                
            if hasattr(self, 'behavior_tab') and self.behavior_tab:
                self.behavior_tab.update_settings()
                
            if hasattr(self, 'text_tab') and self.text_tab:
                self.text_tab.update_settings()
                
            if hasattr(self, 'audio_tab') and self.audio_tab:
                self.audio_tab.update_settings()
                
            if hasattr(self, 'extra_tab') and self.extra_tab:
                self.extra_tab.update_settings()
    
            # الحصول على التاريخ الميلادي (بالأرقام اللاتينية)
            birthdate = self.gregorian_input.date().toString("yyyy-MM-dd")
            
            # تحويل التاريخ إلى الأرقام الإنجليزية
            birthdate = self.convert_date_to_latin(birthdate)
    
            ui_config_path = Path(__file__).resolve().parent.parent / "config" / "ui_settings.json"
            with open(ui_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        
            new_profile = {
                "name_ar": self.name_ar_input.text().strip() or "المستخدم",
                "name_en": self.name_en_input.text().strip() or self.get_system_username(),
                "birthdate": birthdate,  # يتم تخزينه ميلادي بالأرقام الإنجليزية
                "preferences": {
                    "voice_gender": "female",
                    "greeting_style": self.greeting_style_combo.currentText() if hasattr(self, 'greeting_style_combo') else "ودود",
                    "auto_greeting": self.auto_greeting_check.isChecked() if hasattr(self, 'auto_greeting_check') else True,
                    "enable_event_notifications": self.event_notifications_check.isChecked() if hasattr(self, 'event_notifications_check') else True
                }
            }
          
          
            # محاولة الكتابة
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(new_profile, f, ensure_ascii=False, indent=4)
            
            # إظهار رسالة نجاح
            QMessageBox.information(
                self,
                "تم الحفظ بنجاح",
                "تم تحديث إعدادات المستخدم بنجاح!",
                QMessageBox.Ok
            )
            
        except Exception as e:
            # الحصول على تفاصيل الخطأ
            error_details = traceback.format_exc()
            
            # إظهار رسالة خطأ مع تفاصيل المسار والخطأ
            error_msg = (
                f"حدث خطأ أثناء حفظ الإعدادات:\n\n"
                f"الخطأ: {str(e)}\n\n"
                f"المسار: {self.profile_path}\n\n"
                f"تفاصيل تقنية:\n{error_details}"
            )
            
            QMessageBox.critical(
                self,
                "خطأ في الحفظ",
                error_msg,
                QMessageBox.Ok
            )
    

# اختبار النافذة
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dialog = uisettingsmanager()
    
    dialog.show()
    sys.exit(app.exec_())