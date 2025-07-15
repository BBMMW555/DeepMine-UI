from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, QCheckBox, QSpinBox, QComboBox, QLineEdit, QPushButton, QFontComboBox, QColorDialog
from PyQt5.QtGui import QColor

class TextTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # إعدادات النص
        text_group = QGroupBox("✏️ إعدادات النص")
        form_layout = QFormLayout()
        
        # قابلية التعديل
        self.editable_check = QCheckBox("قابل للتعديل")
        self.editable_check.setChecked(self.settings.get("editable", True))
        form_layout.addRow(self.editable_check)
        
        # النص الافتراضي
        self.placeholder_input = QLineEdit()
        self.placeholder_input.setText(self.settings.get("placeholder", "اكتب هنا..."))
        form_layout.addRow("النص الافتراضي:", self.placeholder_input)
        
        # عائلة الخط
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentText(self.settings.get("font_family", "Arial"))
        form_layout.addRow("عائلة الخط:", self.font_family_combo)
        
        # حجم الخط
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 30)
        self.font_size_spin.setValue(self.settings.get("font_size", 12))
        form_layout.addRow("حجم الخط:", self.font_size_spin)
        
        # لون الخط
        self.text_color_button = QPushButton("اختر لون الخط")
        self.text_color_button.clicked.connect(self.choose_text_color)
        self.text_color = QColor(self.settings.get("text_color", "#FFFFFF"))
        form_layout.addRow("لون الخط:", self.text_color_button)
        
        # نمط العرض
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["فوري", "تدريجي", "كتابة"])
        self.display_mode_combo.setCurrentText(self.settings.get("display_mode", "فوري"))
        form_layout.addRow("نمط العرض:", self.display_mode_combo)
        
        # سرعة العرض (فقط للنمط التدريجي والكتابة)
        self.display_speed_spin = QSpinBox()
        self.display_speed_spin.setRange(10, 200)
        self.display_speed_spin.setValue(self.settings.get("display_speed", 50))
        form_layout.addRow("سرعة العرض (حرف/ثانية):", self.display_speed_spin)
        
        # إخفاء النص قبل الانكماش
        self.fade_out_before_shrink = QCheckBox("إخفاء النص قبل الانكماش")
        self.fade_out_before_shrink.setChecked(self.settings.get("fade_out_before_shrink", True))
        form_layout.addRow(self.fade_out_before_shrink)
        
        text_group.setLayout(form_layout)
        layout.addWidget(text_group)
        layout.addStretch()
    
    def choose_text_color(self):
        color = QColorDialog.getColor(self.text_color, self, "اختر لون الخط")
        if color.isValid():
            self.text_color = color

    def update_settings(self):
        self.settings.update({
            "editable": self.editable_check.isChecked(),
            "placeholder": self.placeholder_input.text(),
            "font_family": self.font_family_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "text_color": self.text_color.name(),
            "display_mode": self.display_mode_combo.currentText(),
            "display_speed": self.display_speed_spin.value(),
            "fade_out_before_shrink": self.fade_out_before_shrink.isChecked()
        })