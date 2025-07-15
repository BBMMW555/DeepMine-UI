from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton

class AudioTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # إعدادات الصوت
        audio_group = QGroupBox("🎧 إعدادات الصوت")
        form_layout = QFormLayout()
        
        # جنس الصوت
        self.voice_gender_combo = QComboBox()
        self.voice_gender_combo.addItems(["أنثوي", "ذكوري"])
        self.voice_gender_combo.setCurrentText(self.settings.get("voice_gender", "أنثوي"))
        form_layout.addRow("جنس الصوت:", self.voice_gender_combo)
        
        # لغة الصوت
        self.voice_language_combo = QComboBox()
        self.voice_language_combo.addItems(["العربية", "الإنجليزية", "الفرنسية", "الإسبانية"])
        self.voice_language_combo.setCurrentText(self.settings.get("voice_language", "العربية"))
        form_layout.addRow("لغة الصوت:", self.voice_language_combo)
        
        # جودة الصوت
        self.voice_quality_combo = QComboBox()
        self.voice_quality_combo.addItems(["منخفضة", "متوسطة", "عالية"])
        self.voice_quality_combo.setCurrentText(self.settings.get("voice_quality", "عالية"))
        form_layout.addRow("جودة الصوت:", self.voice_quality_combo)
        
        # جهاز الإخراج الصوتي
        self.audio_output_combo = QComboBox()
        self.audio_output_combo.addItems(["افتراضي", "سماعات الرأس", "مكبرات الصوت"])
        self.audio_output_combo.setCurrentText(self.settings.get("audio_output_device", "افتراضي"))
        form_layout.addRow("جهاز الإخراج:", self.audio_output_combo)
        
        # حفظ صوت المستخدم
        self.save_voice_check = QCheckBox("حفظ عينات صوت المستخدم")
        self.save_voice_check.setChecked(self.settings.get("save_user_voice", False))
        form_layout.addRow(self.save_voice_check)
        
        # مسار حفظ الصوت
        self.voice_path_input = QLineEdit()
        self.voice_path_input.setText(self.settings.get("user_voice_path", "/path/to/save"))
        form_layout.addRow("مسار الحفظ:", self.voice_path_input)
        
        # زر تحديد المسار
        self.browse_button = QPushButton("تصفح...")
        self.browse_button.clicked.connect(self.browse_voice_path)
        form_layout.addRow(self.browse_button)
        
        # نمط تفاعل الميكروفون
        self.mic_interaction_combo = QComboBox()
        self.mic_interaction_combo.addItems(["اضغط للتحدث", "تحدث بدون ضغط"])
        self.mic_interaction_combo.setCurrentText(self.settings.get("mic_interaction_mode", "اضغط للتحدث"))
        form_layout.addRow("نمط الميكروفون:", self.mic_interaction_combo)
        
        audio_group.setLayout(form_layout)
        layout.addWidget(audio_group)
        layout.addStretch()
    
    def browse_voice_path(self):
        # في الواقع، يجب استخدام QFileDialog لاختيار المجلد
        # لكننا سنتركه للتنفيذ لاحقًا
        pass

    def update_settings(self):
        self.settings.update({
            "voice_gender": self.voice_gender_combo.currentText(),
            "voice_language": self.voice_language_combo.currentText(),
            "voice_quality": self.voice_quality_combo.currentText(),
            "audio_output_device": self.audio_output_combo.currentText(),
            "save_user_voice": self.save_voice_check.isChecked(),
            "user_voice_path": self.voice_path_input.text(),
            "mic_interaction_mode": self.mic_interaction_combo.currentText()
        })