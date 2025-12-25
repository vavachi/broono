from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QCheckBox, QDialogButtonBox, QMessageBox, QComboBox, QHBoxLayout, QPushButton, QInputDialog, QLabel, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt
import difflib
from src.core.config import ConfigManager

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Database")
        self.resize(400, 250)
        
        self.config_manager = ConfigManager()
        
        layout = QVBoxLayout(self)
        
        # Profile Selection
        profile_layout = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("Select Profile...")
        self.profile_combo.addItems(self.config_manager.get_all_profiles().keys())
        self.profile_combo.currentTextChanged.connect(self._load_profile)
        
        self.btn_save_profile = QPushButton("Save Profile")
        self.btn_save_profile.clicked.connect(self._save_profile)
        
        profile_layout.addWidget(self.profile_combo)
        profile_layout.addWidget(self.btn_save_profile)
        layout.addLayout(profile_layout)

        form_layout = QFormLayout()
        
        self.server_input = QLineEdit()
        self.db_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.trusted_chk = QCheckBox("Use Trusted Connection (Windows Auth)")
        self.trusted_chk.toggled.connect(self._toggle_auth)
        self.trust_cert_chk = QCheckBox("Trust Server Certificate (for self-signed/Dev)")
        
        form_layout.addRow("Server:", self.server_input)
        form_layout.addRow("Database:", self.db_input)
        form_layout.addRow("Username:", self.user_input)
        form_layout.addRow("Password:", self.pass_input)
        form_layout.addRow("", self.trusted_chk)
        form_layout.addRow("", self.trust_cert_chk)
        
        layout.addLayout(form_layout)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        # Initial state
        self._toggle_auth(False)

    def _toggle_auth(self, checked):
        self.user_input.setEnabled(not checked)
        self.pass_input.setEnabled(not checked)

    def _load_profile(self, name):
        if name == "Select Profile...":
            return
            
        details = self.config_manager.get_profile(name)
        if details:
            self.server_input.setText(details.get('server', ''))
            self.db_input.setText(details.get('database', ''))
            self.user_input.setText(details.get('username', ''))
            self.pass_input.setText(details.get('password', ''))
            self.trusted_chk.setChecked(details.get('trusted', False))
            self.trust_cert_chk.setChecked(details.get('trust_cert', False))

    def _save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile Name:")
        if ok and name:
            details = self.get_details()
            self.config_manager.save_profile(name, details)
            
            # Refresh combo if new
            if self.profile_combo.findText(name) == -1:
                self.profile_combo.addItem(name)
            self.profile_combo.setCurrentText(name)
            QMessageBox.information(self, "Saved", f"Profile '{name}' saved successfully.")

    def get_details(self):
        return {
            'server': self.server_input.text(),
            'database': self.db_input.text(),
            'username': self.user_input.text(),
            'password': self.pass_input.text(),
            'trusted': self.trusted_chk.isChecked(),
            'trust_cert': self.trust_cert_chk.isChecked()
        }

class DiffDialog(QDialog):
    def __init__(self, obj_name, source_def, target_def, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Diff - {obj_name}")
        self.resize(1200, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Header
        header = QLabel(f"Comparing <b>{obj_name}</b>: <span style='color: #d73a49;'>Target (Local)</span> vs <span style='color: #22863a;'>Source (New)</span>")
        header.setStyleSheet("font-size: 11px; margin-bottom: 2px;")
        header.setFixedHeight(50)
        layout.addWidget(header)
        
        # Splitter for side-by-side view
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.left_view = QTextEdit()
        self.left_view.setReadOnly(True)
        self.left_view.setFontFamily("Courier New")
        self.left_view.setFontPointSize(10)
        self.left_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        self.right_view = QTextEdit()
        self.right_view.setReadOnly(True)
        self.right_view.setFontFamily("Courier New")
        self.right_view.setFontPointSize(10)
        self.right_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        self.splitter.addWidget(self.left_view)
        self.splitter.addWidget(self.right_view)
        layout.addWidget(self.splitter)
        
        # Synchronize scrollbars
        self.left_view.verticalScrollBar().valueChanged.connect(self.right_view.verticalScrollBar().setValue)
        self.right_view.verticalScrollBar().valueChanged.connect(self.left_view.verticalScrollBar().setValue)
        
        # Generate diff
        src_text = self._format_def(source_def)
        tgt_text = self._format_def(target_def)
        
        left_html, right_html = self._generate_side_by_side_diff(tgt_text, src_text)
        self.left_view.setHtml(left_html)
        self.right_view.setHtml(right_html)
        
        
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _format_def(self, details):
        if details is None:
            return ""
        if isinstance(details, dict) and 'definition' in details:
            return str(details['definition'])
        if isinstance(details, dict):
            import json
            return json.dumps(details, indent=4)
        return str(details)

    def _generate_side_by_side_diff(self, old_text, new_text):
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        
        left_parts = ["<pre style='font-family: monospace; white-space: pre;'>"]
        right_parts = ["<pre style='font-family: monospace; white-space: pre;'>"]
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    line = self._html_escape(old_lines[i])
                    # Need consistent line height if possible. divs help.
                    left_parts.append(f"<div>{line}</div>")
                    right_parts.append(f"<div>{line}</div>")
            elif tag == 'replace':
                max_len = max(i2 - i1, j2 - j1)
                for k in range(max_len):
                    if i1 + k < i2:
                        left_parts.append(f"<div style='background-color: #ffdce0;'>{self._html_escape(old_lines[i1+k])}</div>")
                    else:
                        left_parts.append("<div style='background-color: #f6f8fa;'>&nbsp;</div>")
                    
                    if j1 + k < j2:
                        right_parts.append(f"<div style='background-color: #dbffdb;'>{self._html_escape(new_lines[j1+k])}</div>")
                    else:
                        right_parts.append("<div style='background-color: #f6f8fa;'>&nbsp;</div>")
            elif tag == 'delete':
                for i in range(i1, i2):
                    left_parts.append(f"<div style='background-color: #ffdce0;'>{self._html_escape(old_lines[i])}</div>")
                    right_parts.append("<div style='background-color: #f6f8fa;'>&nbsp;</div>")
            elif tag == 'insert':
                for j in range(j1, j2):
                    left_parts.append("<div style='background-color: #f6f8fa;'>&nbsp;</div>")
                    right_parts.append(f"<div style='background-color: #dbffdb;'>{self._html_escape(new_lines[j])}</div>")
                    
        left_parts.append("</pre>")
        right_parts.append("</pre>")
        return "".join(left_parts), "".join(right_parts)

    def _html_escape(self, text):
        if not text: return "&nbsp;"
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
