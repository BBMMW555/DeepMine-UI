#UI/settings_tabs/wake_word.py
# وحدة إعدادات كلمات الاستدعاء في واجهة المستخدم
# هذه الوحدة توفر واجهة لتعديل كلمات الاستدعاء التي يستخدمها المساعد الصوتي 
# لتفعيل نفسه، بالإضافة إلى خيارات الاستماع المستمر ووضع الإملاء الصوتي.

import json
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QMessageBox

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QCheckBox

class WakeWordTab(QWidget):
    def __init__(self, wake_words=None, parent=None):
        super().__init__(parent)
        self.wake_words = wake_words or []
        self.setup_ui()
        self.load_wake_words() 

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # كلمات التنبيه
        wake_group = QGroupBox("🔔 كلمات التنبيه (يا مساعد)")
        wake_layout = QVBoxLayout()

        wake_instruction = QLabel("أضف كلمات أو عبارات لاستدعاء المساعد:")
        self.wake_words_list = QListWidget()
        self.wake_words_list.addItems(self.wake_words)

        self.new_wake_input = QLineEdit()
        self.new_wake_input.setPlaceholderText("كلمة أو عبارة جديدة...")

        add_btn = QPushButton("➕ إضافة")
        add_btn.clicked.connect(self.add_wake_word)

        remove_btn = QPushButton("➖ حذف المحدد")
        remove_btn.clicked.connect(self.remove_wake_word)

        wake_layout.addWidget(wake_instruction)
        wake_layout.addWidget(self.wake_words_list)
        wake_layout.addWidget(self.new_wake_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        wake_layout.addLayout(btn_layout)

        wake_group.setLayout(wake_layout)

        # الاستماع المستمر
        listen_group = QGroupBox("👂 وضع الاستماع المستمر")
        listen_layout = QVBoxLayout()
        self.listen_check = QCheckBox("تفعيل الاستماع المستمر (مثل سيري)")
        self.listen_check.setChecked(False)
        listen_layout.addWidget(self.listen_check)
        listen_group.setLayout(listen_layout)

        # وضع الإملاء
        dictation_group = QGroupBox("📝 وضع الإملاء الصوتي")
        dictation_layout = QVBoxLayout()
        self.dictation_check = QCheckBox("تفعيل وضع الإملاء لكتابة الملاحظات الطويلة")
        self.dictation_check.setChecked(True)
        dictation_layout.addWidget(self.dictation_check)
        dictation_group.setLayout(dictation_layout)

        # إضافة المجموعات
        layout.addWidget(wake_group)
        layout.addWidget(listen_group)
        layout.addWidget(dictation_group)
        layout.addStretch()

    def load_wake_words(self):
        """تحميل كلمات الاستدعاء من الملف"""
        path = Path(__file__).resolve().parent.parent.parent / "config" / "wake_word_settings.json"
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.wake_words = data.get("wake_word", {}).get("phrases", [])
                    self.wake_words_list.clear()
                    self.wake_words_list.addItems(self.wake_words)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر تحميل كلمات الاستدعاء: {e}")
    

    def add_wake_word(self):
        """إضافة كلمة استدعاء جديدة"""  
        new_word = self.new_wake_input.text().strip()
        if new_word:    
            if new_word not in self.wake_words:
              
                self.wake_words_list.addItem(new_word)
                self.new_wake_input.clear()
                self.update_wake_words()
            else:
                QMessageBox.warning(self, "تحذير", "هذه الكلمة موجودة بالفعل في القائمة.")


    def save_wake_words(self):
        path = Path(__file__).resolve().parent.parent.parent / "config" / "wake_word_settings.json"
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"wake_word": {"phrases": []}}
            data["wake_word"]["phrases"] = self.wake_words
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر حفظ كلمات الاستدعاء: {e}")


    def remove_wake_word(self):
        """حذف كلمة استدعاء محددة"""
        selected_items = self.wake_words_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.wake_words_list.takeItem(self.wake_words_list.row(item))
            self.update_wake_words()

    def clear_wake_words(self):
        """مسح جميع كلمات الاستدعاء"""
        reply = QMessageBox.question(self, "تأكيد", "هل تريد مسح جميع كلمات الاستدعاء؟", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.wake_words.clear()
            self.wake_words_list.clear()
            self.save_wake_words()


    def update_wake_words(self):
        """تحديث كلمات الاستدعاء من القائمة"""
        self.wake_words = [self.wake_words_list.item(i).text() for i in range(self.wake_words_list.count())]
        self.save_wake_words()
        # يمكنك إزالة رسالة النجاح إذا كانت مزعجة
        # QMessageBox.information(self, "تحديث", "تم تحديث كلمات الاستدعاء بنجاح.")