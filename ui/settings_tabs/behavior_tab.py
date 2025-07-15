from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox

class BehaviorTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = self.convert_settings(settings)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        group = QGroupBox("🚀 سلوك الواجهة")
        form_layout = QFormLayout()
        
        # مهلة الخمول
        self.inactivity_timeout = QSpinBox()
        self.inactivity_timeout.setRange(1, 60)
        self.inactivity_timeout.setValue(self.settings.get("inactivity_timeout", 5))
        form_layout.addRow("مهلة الخمول (ثواني):", self.inactivity_timeout)
        
        # تمكين الانكماش
        self.shrink_enabled = QCheckBox("تمكين الانكماش")
        self.shrink_enabled.setChecked(self.settings.get("shrink_enabled", True))
        form_layout.addRow(self.shrink_enabled)
        
        # مدة الانكماش
        self.shrink_duration = QDoubleSpinBox()
        self.shrink_duration.setRange(0.1, 5.0)
        self.shrink_duration.setSingleStep(0.1)
        self.shrink_duration.setValue(self.settings.get("shrink_duration", 0.5))
        form_layout.addRow("مدة الانكماش (ثواني):", self.shrink_duration)
        
        # الاختفاء بعد الانكماش
        self.hide_after_shrink = QCheckBox("الاختفاء بعد الانكماش")
        self.hide_after_shrink.setChecked(self.settings.get("hide_after_shrink", True))
        form_layout.addRow(self.hide_after_shrink)
        
        # مدة الاختفاء
        self.hide_duration = QSpinBox()
        self.hide_duration.setRange(1, 60)
        self.hide_duration.setValue(self.settings.get("hide_duration", 5))
        form_layout.addRow("مدة الاختفاء (ثواني):", self.hide_duration)
        
        # نسبة الانكماش أثناء الكلام
        self.shrink_percentage = QSpinBox()
        self.shrink_percentage.setRange(1, 50)
        self.shrink_percentage.setValue(self.settings.get("shrink_percentage_speaking", 5))
        form_layout.addRow("نسبة الانكماش أثناء الكلام (%):", self.shrink_percentage)
        
        # إيقاف الحركة أثناء الاستماع
        self.pause_animation = QCheckBox("إيقاف الحركة أثناء الاستماع")
        self.pause_animation.setChecked(self.settings.get("pause_animation_listening", True))
        form_layout.addRow(self.pause_animation)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        
    def convert_settings(self, settings):
        """تحويل الإعدادات إلى قاموس إذا كانت من نوع set"""
        if isinstance(settings, set):
            # هنا يمكنك تحديد القيم الافتراضية لكل إعداد
            return {
                "inactivity_timeout": 5,
                "shrink_enabled": True,
                "shrink_duration": 0.5,
                "hide_after_shrink": True,
                "hide_duration": 5,
                "shrink_percentage_speaking": 5,
                "pause_animation_listening": True
            }
        elif isinstance(settings, dict):
            return settings
        else:
            return {}

    def update_settings(self):
        self.settings.update({
            "inactivity_timeout": self.inactivity_timeout.value(),
            "shrink_enabled": self.shrink_enabled.isChecked(),
            "shrink_duration": self.shrink_duration.value(),
            "hide_after_shrink": self.hide_after_shrink.isChecked(),
            "hide_duration": self.hide_duration.value(),
            "shrink_percentage_speaking": self.shrink_percentage.value(),
            "pause_animation_listening": self.pause_animation.isChecked()
        })   