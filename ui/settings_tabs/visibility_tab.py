from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QCheckBox
from PyQt5.QtCore import Qt
import json

class VisibilityTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        # تحويل الإعدادات إلى dict إذا كانت من نوع set
        self.settings = self.convert_settings(settings)
        self.init_ui()
    
    def convert_settings(self, settings):
        """تحويل الإعدادات إلى قاموس إذا كانت من نوع set"""
        if isinstance(settings, set):
            return {item: True for item in settings}
        elif isinstance(settings, dict):
            return settings
        else:
            return {}
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        group = QGroupBox("👁️ إظهار العناصر")
        grid_layout = QGridLayout()
        
        # عناصر الرؤية
        self.visibility_text_box = QCheckBox()
        self.visibility_icon = QCheckBox()
        self.visibility_mic_button = QCheckBox()
        self.visibility_settings_button = QCheckBox()
        self.visibility_mini_icon_on_interaction = QCheckBox()
        self.visibility_cursor_tracking_icon = QCheckBox()
        
        visibility_items = [
            ("مربع النص", self.visibility_text_box),
            ("الأيقونة الرئيسية", self.visibility_icon),
            ("زر الميكروفون", self.visibility_mic_button),
            ("زر الإعدادات", self.visibility_settings_button),
           # ("أيقونة مصغرة أثناء التفاعل", self.visibility_minي_icon_on_interaction),
            ("أيقونة تتبع المؤشر", self.visibility_cursor_tracking_icon),
        ]
        
        for row, (label, widget) in enumerate(visibility_items):
            key = label.replace(" ", "_")
            widget.setChecked(self.settings.get(key, True))
            grid_layout.addWidget(QLabel(label), row, 0)
            grid_layout.addWidget(widget, row, 1)
        
        group.setLayout(grid_layout)
        layout.addWidget(group)
        layout.addStretch()


    def update_settings(self):
        self.settings.update({
            "text_box": self.visibility_text_box.isChecked(),
            "icon": self.visibility_icon.isChecked(),
            "mic_button": self.visibility_mic_button.isChecked(),
            "settings_button": self.visibility_settings_button.isChecked(),
            "mini_icon_on_interaction": self.visibility_mini_icon_on_interaction.isChecked(),
            "cursor_tracking_icon": self.visibility_cursor_tracking_icon.isChecked()
        })    