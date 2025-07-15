from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, QSpinBox, QComboBox

class ExtraTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # إعدادات إضافية
        extra_group = QGroupBox("⚙️ إعدادات إضافية")
        form_layout = QFormLayout()
        
        # سرعة الرسوم المتحركة
        self.animation_speed_combo = QComboBox()
        self.animation_speed_combo.addItems(["بطيء", "متوسط", "سريع"])
        self.animation_speed_combo.setCurrentText(self.settings.get("animation_speed", "متوسط"))
        form_layout.addRow("سرعة الرسوم المتحركة:", self.animation_speed_combo)
        
        # الموقع الافتراضي
        self.position_x_spin = QSpinBox()
        self.position_x_spin.setRange(0, 1920)
        self.position_x_spin.setValue(self.settings.get("position", [1139, 299])[0])
        self.position_y_spin = QSpinBox()
        self.position_y_spin.setRange(0, 1080)
        self.position_y_spin.setValue(self.settings.get("position", [1139, 299])[1])
        
        form_layout.addRow("الموقع الأفقي (X):", self.position_x_spin)
        form_layout.addRow("الموقع الرأسي (Y):", self.position_y_spin)
        
        extra_group.setLayout(form_layout)
        layout.addWidget(extra_group)
        layout.addStretch()
    
    def update_settings(self):
        self.settings.update({
            "animation_speed": self.animation_speed_combo.currentText(),
            "position": [self.position_x_spin.value(), self.position_y_spin.value()]
        })