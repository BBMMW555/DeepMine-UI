import winsound
import time
from PyQt5.QtCore import pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QDesktopWidget
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QApplication
from pathlib import Path
import os
from PyQt5.QtWidgets import QStyle
import datetime

class UIManager:
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        # تعريف المؤقتات أولاً
        self.hide_timer = QTimer()
        self.idle_timer = QTimer()
        self.shrink_timer = QTimer()
        self.shrink_wait_timer = QTimer()
        
        # ثم تهيئتها
        self.setup_timers()
        self.setup_tray()
        self.original_icon_size = parent_ui.animation_label.size()
        self.original_size = parent_ui.size()
        self.last_interaction_time = time.time()
        self.is_shrinking = False
        self.shrink_complete = False
        
        print(f"هل صينية النظام متاحة؟ {QSystemTrayIcon.isSystemTrayAvailable()}")
        print(f"هل صينية النظام تدعم الرسائل؟ {QSystemTrayIcon.supportsMessages()}")

    def setup_timers(self):
        self.log_step("بدأ عرض الواجهة (تهيئة المؤقتات)")
        
        # ربط المؤقتات بالإشارات
        self.hide_timer.timeout.connect(self.fade_out)
        self.idle_timer.timeout.connect(self.check_idle)
        self.shrink_timer.timeout.connect(self.shrink_icon_step)
        self.shrink_wait_timer.timeout.connect(self.after_shrink_wait)
        
        # بدء مؤقت الخمول
        self.idle_timer.start(1000)
    
    def setup_tray(self):
        self.log_step("بدأ عرض الواجهة (تهيئة صينية النظام)")
        
        self.tray_icon = QSystemTrayIcon(self.parent_ui)
        
        try:
            # المسار الصحيح من جذر المشروع
            base_dir = Path(__file__).resolve().parent.parent.parent  # العودة 3 مستويات
            icon_path = base_dir / "assets" / "icons" / "icon.png"
            
            self.log_step(f"مسار الأيقونة: {icon_path}")
            
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
            else:
                raise FileNotFoundError(f"ملف الأيقونة غير موجود في: {icon_path}")
                
        except Exception as e:
            self.log_step(f"⚠️ تحذير: {str(e)}")
            self.tray_icon.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))
        
        menu = QMenu()
        menu.addAction("إظهار المساعد", self.fade_in)
        menu.addAction("فتح الإعدادات", self.parent_ui.show_settings)
        menu.addAction("خروج", QApplication.quit)
        self.tray_icon.setContextMenu(menu)
        
        # تفعيل الأيقونة
        self.tray_icon.show()
        self.log_step("تم تفعيل أيقونة الصينية")
       
        self.tray_icon.activated.connect(self.handle_tray_click)

   

    def fade_out(self):
        # توقف إذا كانت الواجهة مخفية بالفعل
        if not self.parent_ui.isVisible():
            self.log_step("❎ الواجهة مخفية بالفعل، لا حاجة للإخفاء")
            return

        # توقف إذا كانت الحركة جارية
        if hasattr(self, "fade_out_animation") and self.fade_out_animation.state() == QPropertyAnimation.Running:
            self.log_step("⏳ الإخفاء جارٍ بالفعل، تجاهل الطلب")
            return

        self.log_step("🔽 بدأ الإخفاء التدريجي")

        # بدء الحركة التدريجية
        self.fade_out_animation = QPropertyAnimation(self.parent_ui, b"windowOpacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.finalize_hide)
        self.fade_out_animation.start()

        if not self.parent_ui.isVisible():
            return  # فقط تجاهل بصمت
        
    def finalize_hide(self):
        self.log_step("تم إخفاء الواجهة بالكامل (finalize_hide)")
        self.parent_ui.hide()
        self.is_shrinking = False
        self.shrink_complete = False
        
        # إعادة تعيين حجم النافذة بعد الإخفاء
        self.parent_ui.setFixedSize(self.original_size)
        self.parent_ui.animation_label.setFixedSize(self.original_icon_size)
        self.parent_ui.movie.setScaledSize(self.original_icon_size)
    
    def record_interaction(self):
        """تسجيل تفاعل المستخدم وإعادة تعيين المؤقتات"""
        self.log_step("تم تسجيل تفاعل المستخدم")
        self.last_interaction_time = time.time()
        self.reset_timers()

    def fade_in(self):
     # بدلاً من عملية الظهور التدريجي، نستخدم الظهور الفوري
       self.show_immediately()

    def check_idle(self):
        if not self.parent_ui.isVisible():
            return
            
        current_time = time.time()
        idle_seconds = current_time - self.last_interaction_time
        
        # إذا اكتمل الانكماش ومرت 5 ثوان
        if self.shrink_complete and idle_seconds > 10:
            self.log_step("انتهى وقت الانتظار بعد الانكماش، بدء الإخفاء")
            self.fade_out()
            self.shrink_complete = False
            return
            
        # إخفاء المكونات بعد 10 ثواني من عدم التفاعل
        if idle_seconds > 10 and self.parent_ui.message_frame.isVisible():
            self.log_step("إخفاء مكونات الواجهة (تجاوز 10 ثواني)")
            self.hide_ui_components()
            self.start_shrink_process()
        
        # بدء الانكماش إذا مرت 10 ثواني ولم يبدأ بعد
        elif idle_seconds > 10 and not self.is_shrinking:
            self.log_step("بدء عملية التصغير (تجاوز 10 ثواني)")
            self.start_shrink_process()

    def hide_ui_components(self):
        self.log_step("بدأ عرض الواجهة (إخفاء مكونات الواجهة)")

        if self.parent_ui.message_frame.isVisible():
            self.parent_ui.message_frame.hide()
            self.parent_ui.mic_button.hide()
            self.parent_ui.settings_button.hide()
            self.parent_ui.update()

    def handle_tray_click(self, reason):
        self.log_step(f"نقر صينية النظام: {reason}")
        
        reason_dict = {
            0: "Unknown",
            1: "Context (Right Click)",
            2: "Double Click",
            3: "Trigger (Left Click)",
            4: "Middle Click"
        }
        reason_text = reason_dict.get(reason, f"Unknown ({reason})")
        self.log_step(f"نقر صينية النظام: {reason_text}")
        
        if reason == QSystemTrayIcon.Trigger:  # 3 - النقر الأيسر
            self.log_step("نقر رئيسي على الأيقونة (يسار)")
            self.show_immediately()  # استدعاء دالة الظهور الفوري
        elif reason == QSystemTrayIcon.Context:  # 1 - النقر الأيمن
            self.log_step("نقر سياقي (يمين) على الأيقونة")
        elif reason == QSystemTrayIcon.DoubleClick:  # 2 - النقر المزدوج
            self.log_step("نقر مزدوج على الأيقونة")
            self.show_immediately()  # استدعاء دالة الظهور الفوري
        else:
            self.log_step(f"نقر غير معالج: {reason_text}")
    
    def show_immediately(self):
        """إظهار الواجهة فوراً دون تأخير أو حركات تدريجية"""
     
        # إذا كانت الواجهة غير ظاهرة (اختفاء كامل)
        if not self.parent_ui.isVisible():
            self.log_step("العودة بعد اختفاء كامل، سيتم إظهار الواجهة فورًا بالحالة الأخيرة")
     
            # عرض الأيقونة بالحالة السابقة (منكمشة أو كاملة)
            self.parent_ui.setFixedSize(self.original_size)
            self.parent_ui.animation_label.setFixedSize(self.original_icon_size)
            self.parent_ui.movie.setScaledSize(self.original_icon_size)              

            # إظهار المكونات حسب الانكماش
            self.parent_ui.message_frame.setVisible(True)
            self.parent_ui.mic_button.setVisible(True)
            self.parent_ui.settings_button.setVisible(True)
     
            self.parent_ui.setWindowOpacity(1.0)
            self.parent_ui.show()
            self.parent_ui.raise_()
            self.parent_ui.activateWindow()
     
            greetings = [
                "👋 رجعت لك يا مهندس بسّام، جاهز لأي شيء!",
                "👋 أنا بانتظارك... قل لي ما تحتاج 🔎"
            ]
            import random
            self.parent_ui.add_message(random.choice(greetings))
     
            self.reset_timers()
            self.last_interaction_time = time.time()
            return  # انتهى العرض من حالة الاختفاء
     
        # حالة العرض الفوري العادية (مثلاً أثناء الانكماش)
        self.log_step("بدأ عرض الواجهة (ظهور فوري)")
     
        self.idle_timer.stop()
        self.shrink_timer.stop()
        self.shrink_wait_timer.stop()
        self.hide_timer.stop()
     
        self.parent_ui.setFixedSize(self.original_size)
        
        self.parent_ui.animation_label.setFixedSize(self.original_icon_size)
        self.parent_ui.movie.setScaledSize(self.original_icon_size) 
        
     
        # إظهار جميع المكونات
        self.parent_ui.message_frame.setVisible(True)
        self.parent_ui.mic_button.setVisible(True)
        self.parent_ui.settings_button.setVisible(True)
     
        self.is_shrinking = False
        self.shrink_complete = False
     
        try:
            # إعادة تحريك النافذة إلى المركز
            screen = QDesktopWidget().availableGeometry()
            self.parent_ui.move(
                (screen.width() - self.parent_ui.width()) // 2,
                (screen.height() - self.parent_ui.height()) // 2
            )
            self.log_step("تم تحريك النافذة إلى المركز")
        except Exception as e:
            print(f"خطأ في تحريك النافذة: {e}")
     
        greetings = [
            "👋 مرحباً مجدداً بالمهندس بسّام، هل تحتاج مساعدة؟",
            "👋 أهلاً وسهلاً، كيف يمكنني مساعدتك اليوم؟",
            "👋 مساء الخير، هل هناك أمر معين تريده؟",
            "👋 أهلاً بك، هل لديك طلب أو استفسار؟",
            "👋 عوداً حميداً، هل تبحث عن شيء معين؟"
        ]
        import random
        self.parent_ui.add_message(random.choice(greetings))
     
        self.parent_ui.setWindowOpacity(1.0)
        self.parent_ui.show()
        self.parent_ui.raise_()
        self.parent_ui.activateWindow()
     
        self.last_interaction_time = time.time()
        self.idle_timer.start(1000)
        self.log_step("تم عرض الواجهة فوراً")


#------------------ بدء عملية الانكماش ------------------------------
    def start_shrink_process(self):
        if self.is_shrinking:
            return
            
        self.log_step("بدأ عرض الواجهة (بدء عملية تصغير الأيقونة)")
        self.is_shrinking = True
        self.shrink_complete = False

        # إخفاء المكونات إذا كانت ظاهرة
        if self.parent_ui.message_frame.isVisible():
            self.hide_ui_components()
        
        self.current_size = self.parent_ui.animation_label.size()
        
        # إذا كانت الأيقونة منكمشة بالفعل
        if self.current_size.width() <= 100:
            self.log_step("الأيقونة منكمشة بالفعل، بدء الانتظار")
            self.after_shrink_wait()
            return
            
        # بدأ عملية الانكماش
        self.shrink_timer.start(50)

  #------------------ إظهار الأيقونة في صينية النظام ------------------------------
    def shrink_icon_step(self):
        if not self.is_shrinking:
            self.shrink_timer.stop()
            return
            
        step = 2
        if self.current_size.width() > 100:
            self.current_size = QSize( 
                self.current_size.width() - step,
                self.current_size.height() - step
            )
            self.parent_ui.animation_label.setFixedSize(self.current_size) 
            self.parent_ui.movie.setScaledSize(self.current_size)
            self.parent_ui.animation_label.update()  # إضافة تحديث فوري
        else:
            self.log_step("اكتمل الانكماش، بدء الانتظار")
            self.shrink_timer.stop()
            self.after_shrink_wait()
    
    # ------------------ الانتظار بعد الانكماش ------------------------------
    def after_shrink_wait(self):
        self.log_step("بدء الانتظار لمدة 5 ثوان بعد الانكماش")
        self.shrink_complete = True
        self.last_interaction_time = time.time()

    def reset_timers(self):
        # إيقاف جميع المؤقتات أولاً
        self.idle_timer.stop()
        self.shrink_timer.stop()
        self.shrink_wait_timer.stop()
        self.hide_timer.stop()
        
        self.log_step("بدأ عرض الواجهة (إعادة تعيين المؤقتات)")
        
        self.is_shrinking = False
        self.shrink_complete = False
        
        # إعادة تشغيل مؤقت الخمول فقط
        self.idle_timer.start(1000) 
        self.last_interaction_time = time.time()

    def log_step(self, label):
        # تجاهل الرسائل المتكررة
        if hasattr(self, "last_log") and self.last_log == label:
            return
            
        self.last_log = label
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 📍 {label}")

    def cleanup(self):
        self.hide_timer.deleteLater()
        self.idle_timer.deleteLater()