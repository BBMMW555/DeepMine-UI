import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from PyQt5.QtCore import (pyqtSignal, Qt, pyqtSlot, QPropertyAnimation, 
                         QEasingCurve, QSize, QUrl, QTimer)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                            QSystemTrayIcon, QMenu, QSizePolicy,
                            QDesktopWidget, QVBoxLayout, QScrollArea, QFrame)
from PyQt5.QtGui import QMovie, QIcon, QFont
from PyQt5.QtMultimedia import QSoundEffect

from core_engine.utilities.text_manager import TextManager
from core_engine.ui_interaction.ui_manager import UIManager
from core_engine.ui_interaction.interaction_manager import InteractionManager



PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_asset_path(*path_parts):
    """مساعدة للحصول على مسار الملفات في مجلد assets"""
    return str(PROJECT_ROOT / "assets" / Path(*path_parts))
# ... بقية الكود بدون تغيير ...
class MessageBubble(QLabel):
    """فقاعة رسالة مخصصة تشبه الدردشة"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet("""
            background-color: rgba(0, 120, 215, 0.2);       
            border-radius: 12px;
            padding: 8px 12px;
            color: white;
            font-size: 13px;
            font-weight: bold;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.setMargin(5)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        
        # تحديد حجم الفقاعة بناءً على المحتوى
        font_metrics = self.fontMetrics()
        text_width = font_metrics.boundingRect(self.text()).width() + 40
        self.setMinimumWidth(min(text_width, parent.width() - 40))
        self.setMaximumWidth(parent.width() - 30)

class MainWindow(QWidget):
    command_received_signal = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, speech_manager, command_handler, context_manager, 
                 uisettings_manager, settings_manager):
        super().__init__()
        
        # النظام التشغيلي الحالي (يتم الكشف تلقائياً)
        self.current_os = self.detect_os()
        
        # تهيئة الواجهة أولاً
        self.setup_ui()
        
        # ثم تهيئة المديرين
        self.init_managers(speech_manager, command_handler, context_manager, 
                         uisettings_manager, settings_manager)
        
        self.setup_animations()
        self.setup_sound_system()
        self.move_to_center()
        
        # إظهار الترحيب الأولي بعد تأخير قصير
        QTimer.singleShot(300, self.show_welcome)
        
        # حل مؤقت لمشكلة ui_manager
        self.response_display = QLabel(self)
        self.response_display.setVisible(False)

    def detect_os(self):
        """الكشف عن النظام التشغيلي الحالي"""
        if sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('win'):
            return 'windows'
        elif sys.platform.startswith('darwin'):
            return 'macos'
        elif 'android' in sys.platform.lower():
            return 'android'
        else:
            return 'unknown'

    def init_managers(self, speech_manager, command_handler, context_manager,
                     uisettings_manager, settings_manager):
        """تهيئة جميع المديرين"""
        self.speech_manager = speech_manager
        self.command_handler = command_handler
        self.context_manager = context_manager
        self.settings = settings_manager
        self.uisettings = uisettings_manager
        self.text_manager = TextManager()
        self.ui_manager = UIManager(self)
        self.interaction_manager = InteractionManager(
            self.text_manager, 
            self.speech_manager,
            parent=self
        )

    def setup_ui(self):
        """تهيئة واجهة المستخدم مع تعديلات حسب النظام"""
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        if self.current_os == 'android':
            flags |= Qt.MaximizeUsingFullscreenGeometryHint
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # حجم مناسب لجميع الأجهزة
        screen_size = QDesktopWidget().availableGeometry()
        base_width = min(300, screen_size.width() * 0.8) # 80% من عرض الشاشة
        base_height = min(500, screen_size.height() * 0.7) # 70% من ارتفاع الشاشة
        self.setFixedSize(int(base_width), int(base_height))
        
        # المكونات المرنة
        self.setup_ui_components()

    def setup_ui_components(self):
        """إنشاء مكونات الواجهة مع تكيف تلقائي"""
        # 1. الأزرار والأيقونة في الأسفل (جنباً إلى جنب)
        self.setup_bottom_elements()
        
        # 2. حاوية الرسائل فوق الأيقونة مباشرة
        self.setup_message_container()


    def setup_animation_label(self):
        """تهيئة الأيقونة المتحركة في مركز الواجهة"""
        icon_size = min(self.width() * 0.6, self.height() * 0.5)  # # 60% من العرض أو 50% من الارتفاع
        self.animation_label = QLabel(self) # إنشاء QLabel للأيقونة
        self.animation_label.setGeometry(
            int((self.width() - icon_size) // 2), # مركز أفقي
            int((self.height() - icon_size) // 2), # مركز عمودي
            int(icon_size),
            int(icon_size)
        )
                
        # حل مشكلة تحميل الأيقونة باستخدام المسار المطلق
        base_dir = Path(__file__).resolve().parent.parent
        icon_path = base_dir / "assets" / "icons" / "voic.gif"
        
        self.movie = QMovie(str(icon_path))
        self.movie.setScaledSize(QSize(int(icon_size), int(icon_size)))
        self.animation_label.setMovie(self.movie)
        self.movie.start()
    
    def setup_bottom_elements(self):
        """تهيئة الأزرار والأيقونة في أسفل الواجهة مع الأزرار تحت الأيقونة مباشرة"""
        # حجم الأيقونة
        icon_size = min(self.width() * 0.6, self.height() * 0.6) 
        
        # حجم الأزرار
        button_size = min(44, self.width() * 0.15)
        
        # الموضع الرأسي للأيقونة في الأسفل
        vertical_position_icon = self.height() - icon_size - 50
        
        # الموضع الرأسي للأزرار (تحت الأيقونة مباشرة)
        vertical_position_buttons = vertical_position_icon + icon_size + 5  # 10px تحت الأيقونة
        
        # حل مشكلة تحميل الأيقونة باستخدام المسار المطلق
        base_dir = Path(__file__).resolve().parent.parent
        
        # 1. الأيقونة (في المنتصف)
        self.animation_label = QLabel(self)
        self.animation_label.setGeometry(
            int((self.width() - icon_size) // 2),
            int(vertical_position_icon),
            int(icon_size),
            int(icon_size)
        )
        
        icon_path = base_dir / "assets" / "icons" / "voic.gif"
        self.movie = QMovie(str(icon_path))
        self.movie.setScaledSize(QSize(int(icon_size), int(icon_size)))
        self.animation_label.setMovie(self.movie)
        self.movie.start()
        
        # 2. زر الإعدادات (على اليسار)
        self.settings_button = QPushButton(self)
        settings_icon_path = base_dir / "assets" / "icons" / "settings.png"
        self.settings_button.setIcon(QIcon(str(settings_icon_path)))
        self.settings_button.setIconSize(QSize(int(button_size * 0.6), int(button_size * 0.6)))
        self.settings_button.setGeometry(
            int(self.width() * 0.3 - button_size // 2),
            int(vertical_position_buttons),
            int(button_size),
            int(button_size))
        self.settings_button.clicked.connect(self.show_settings)
        
        # 3. زر الميكروفون (على اليمين)
        self.mic_button = QPushButton(self)
        mic_icon_path = base_dir / "assets" / "icons" / "mic.png"
        self.mic_button.setIcon(QIcon(str(mic_icon_path)))
        self.mic_button.setIconSize(QSize(int(button_size * 0.6), int(button_size * 0.6)))
        self.mic_button.setGeometry(
            int(self.width() * 0.7 - button_size // 2),
            int(vertical_position_buttons),
            int(button_size),
            int(button_size)
        )  
        self.mic_button.clicked.connect(self.start_listening)
        
        # تنسيق موحد للأزرار
        button_style = """
            QPushButton {
                background-color: rgba(0, 120, 215, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: %dpx;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 215, 0.35);
            }
        """ % (button_size // 2)
        
        self.mic_button.setStyleSheet(button_style)
        self.settings_button.setStyleSheet(button_style)
    
    def setup_message_container(self):
        """إنشاء حاوية للرسائل فوق الأيقونة مباشرة وملاصقة لها"""
        # حساب موقع أعلى الحاوية (في أعلى النافذة)
        container_top = 10
        
        # حساب ارتفاع الحاوية (حتى أعلى الأيقونة مباشرة)
        container_height = self.animation_label.y() - container_top - 5  # 5px فوق الأيقونة
        
        # إنشاء إطار للحاوية
        self.message_frame = QFrame(self)
        self.message_frame.setGeometry(
            10,  # مسافة من اليسار
            container_top,  # مسافة من الأعلى
            self.width() - 20,  # عرض الحاوية
            container_height  # ارتفاع الحاوية
        )
        self.message_frame.setStyleSheet("""
            background: transparent;
            border: none; 
        """)
        
        # إنشاء منطقة التمرير
        self.scroll_area = QScrollArea(self.message_frame)
        self.scroll_area.setGeometry(0, 0, self.message_frame.width(), self.message_frame.height())
        self.scroll_area.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # إنشاء حاوية المحتوى
        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        self.content_widget.setStyleSheet("background: transparent;")
        
        # إنشاء تخطيط عمودي للرسائل
        self.message_layout = QVBoxLayout(self.content_widget) 
        self.message_layout.setSpacing(4)  # تقليل المسافة بين الرسائل
        self.message_layout.setContentsMargins(3, 3, 3, 3)  # تقليل الهوامش
        self.message_layout.setAlignment(Qt.AlignTop)
        
        # إضافة عنصر ممتد لدفع الرسائل لأعلى
        self.message_layout.addStretch(1)

    def add_message(self, text):
        self.clear_messages()
        """إضافة رسالة جديدة إلى الحاوية (من الأسفل)"""
        bubble = MessageBubble(text, self.content_widget)
        
        # إضافة الرسالة في نهاية التخطيط (الأسفل)
        self.message_layout.addWidget(bubble)
        
        # التمرير إلى الأسفل لعرض الرسالة الجديدة
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def clear_messages(self):
        """مسح جميع الرسائل في الحاوية"""
        for i in reversed(range(self.message_layout.count())):
            widget = self.message_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
    
    
    def setup_animations(self):
        """تهيئة الرسوم المتحركة"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def setup_sound_system(self):
        """تهيئة نظام الصوت المتوافق مع جميع الأنظمة"""
        self.sound_effect = QSoundEffect()
        
        # حل مشكلة تحميل الصوت باستخدام المسار المطلق
        base_dir = Path(__file__).resolve().parent.parent  # العودة لمستويين فقط
        sound_path = base_dir / "assets" / "sounds" / "peep.mp3"
        
        if sound_path.exists():
            self.sound_effect.setSource(QUrl.fromLocalFile(str(sound_path)))
        else:
            print(f"⚠️ تحذير: ملف الصوت غير موجود في: {sound_path}")
        
    def move_to_center(self):
        """تحريك النافذة إلى المركز مع مراعاة حجم الشاشة"""
        screen = QDesktopWidget().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    @pyqtSlot(str)
    def handle_command(self, command):
        """معالجة الأوامر الواردة"""
        try:
            response = self.command_handler.handle(command)
            if message := response.get("data", {}).get("message") or response.get("data", {}).get("text_ar"):
                self.add_message(message)
            
            if response.get("type") == "action" and (action := response.get("data", {}).get("action")):
                self.ui_manager.execute_action(action)
                
        except Exception as e:
            self.add_message("حدث خطأ أثناء معالجة الأمر")

    def start_listening(self):
        """بدء الاستماع للأوامر الصوتية"""
        if hasattr(self, 'speech_manager') and self.speech_manager:
            # تشغيل صوت التنبيه
            if hasattr(self.speech_manager, 'audio_responses'):
                self.speech_manager.audio_responses.play('wake')
                
            self.speech_manager.start_listening(self.command_received_signal.emit)
            self.add_message("🎤 جاهز للاستماع...")
        else:
            self.add_message("⚠️ نظام الصوت غير متاح")

    def show_welcome(self, context=None):
        """عرض رسالة ترحيب حسب الوقت والسياق"""
        greeting = self.text_manager.get_greeting(context)
        self.add_message(f"{greeting['text_ar']}\n\n{greeting['text_en']}")
        
        # تشغيل الصوت فقط إذا تم تحميله بنجاح
        if self.sound_effect.source().isValid():
            self.sound_effect.play()

    def show_settings(self):
        """عرض نافذة الإعدادات"""
        dialog = self.uisettings(self)
        if dialog.exec_():
            self.ui_manager.apply_settings(dialog.settings)

    def mousePressEvent(self, event):
        """التعامل مع ضغط الماوس للتحريك"""
        self.old_pos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        """تحريك النافذة عند السحب"""
        delta = event.globalPos() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تهيئة المديرين الأساسيين (يمكن استبدالها بالتنفيذ الفعلي)
    main_window = MainWindow(
        speech_manager=None,
        command_handler=None,
        context_manager=None,
        uisettings_manager=None,
        settings_manager=None
    )
    
    main_window.show()
    sys.exit(app.exec_())