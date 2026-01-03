from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QTextEdit, QTreeWidget, 
                             QTreeWidgetItem, QMessageBox, QSplitter, QLineEdit, QFileDialog, QMenu, QHeaderView,
                             QCheckBox, QDateEdit)
from PyQt6.QtCore import Qt, QPoint, QDate
import json
from datetime import datetime
from src.db.connector import DbConnector
from src.db.schema import SchemaExtractor
from src.core.compare import SchemaComparer
from src.core.generator import ScriptGenerator
from src.ui.dialogs import ConnectionDialog, DiffDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Broono")
        self.resize(1100, 750)
        
        # State
        self.source_connector = DbConnector()
        self.target_connector = DbConnector()
        self.diff = None
        self.source_schema = None
        self.target_schema = None
        self.object_filter = None # Set of object names (schema.object)
        
        # UI Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        title_lbl = QLabel("Broono")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #1d4ed8;")
        sub_title_lbl = QLabel("MSSQL Schema comparison tool")
        sub_title_lbl.setStyleSheet("font-size: 11px; color: #3b82f6; margin-bottom: 5px;")
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(sub_title_lbl)
        main_layout.addLayout(header_layout)
        
        # 1. Connection Area (Compact Horizontal)
        self.conn_area = QGroupBox()
        conn_box_layout = QVBoxLayout(self.conn_area)
        conn_box_layout.setContentsMargins(10, 5, 10, 10)
        conn_box_layout.setSpacing(5)
        
        box_title = QLabel("DATABASE CONNECTIONS")
        box_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #475569; letter-spacing: 1px;")
        conn_box_layout.addWidget(box_title)
        
        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(10)
        
        # Source
        src_lbl = QLabel("<b>Source:</b>")
        self.src_status = QLabel("Not Connected")
        self.src_status.setStyleSheet("color: #ef4444")
        btn_src_conn = QPushButton("🔌 Connect...")
        btn_src_conn.setFixedWidth(100)
        btn_src_conn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_src_conn.clicked.connect(lambda: self.open_connection_dialog(self.source_connector, self.src_status))
        
        # Target
        tgt_lbl = QLabel("<b>Target:</b>")
        self.tgt_status = QLabel("Not Connected")
        self.tgt_status.setStyleSheet("color: #ef4444")
        btn_tgt_conn = QPushButton("🔌 Connect...")
        btn_tgt_conn.setFixedWidth(100)
        btn_tgt_conn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tgt_conn.clicked.connect(lambda: self.open_connection_dialog(self.target_connector, self.tgt_status))
        
        conn_layout.addWidget(src_lbl)
        conn_layout.addWidget(self.src_status, 1)
        conn_layout.addWidget(btn_src_conn)
        conn_layout.addSpacing(30)
        conn_layout.addWidget(tgt_lbl)
        conn_layout.addWidget(self.tgt_status, 1)
        conn_layout.addWidget(btn_tgt_conn)
        
        conn_box_layout.addLayout(conn_layout)
        main_layout.addWidget(self.conn_area)
        
        # 2. Action Area
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        self.btn_compare = QPushButton("🔍 Compare Schemas")
        self.btn_compare.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_compare.clicked.connect(self.run_comparison)
        
        self.btn_load_list = QPushButton("📂 Load Object List...")
        self.btn_load_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_list.clicked.connect(self.load_object_list)
        
        self.btn_clear_list = QPushButton("❌ Clear List")
        self.btn_clear_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_list.clicked.connect(self.clear_object_list)
        self.btn_clear_list.setEnabled(False)
        
        self.btn_generate = QPushButton("🚀 Generate Script")
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.generate_script)
        self.btn_generate.setEnabled(False)
        
        self.btn_save_comp = QPushButton("💾 Save Comp.")
        self.btn_save_comp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_comp.clicked.connect(self.save_comparison)
        self.btn_save_comp.setEnabled(False)
        
        self.btn_load_comp = QPushButton("📁 Load Comp.")
        self.btn_load_comp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_comp.clicked.connect(self.load_comparison)
        
        action_layout.addWidget(self.btn_compare)
        action_layout.addWidget(self.btn_generate)

        # Date Filter
        self.chk_date_filter = QCheckBox("Changes from:")
        self.chk_date_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_date_filter.stateChanged.connect(self.toggle_date_filter)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setEnabled(False)

        action_layout.addWidget(self.chk_date_filter)
        action_layout.addWidget(self.date_edit)
        
        action_layout.addStretch(1) # Gap between primary and secondary
        
        action_layout.addWidget(self.btn_load_list)
        action_layout.addWidget(self.btn_clear_list)
        action_layout.addWidget(self.btn_save_comp)
        action_layout.addWidget(self.btn_load_comp)
        main_layout.addLayout(action_layout)
        
        # 3. Results Area (Splitter for Tree vs Script)
        self.results_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Search + Tree
        tree_container = QWidget()
        tree_container_layout = QVBoxLayout(tree_container)
        tree_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search objects...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_tree)
        tree_container_layout.addWidget(self.search_input)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Object", "Change Type", "Details"])
        self.tree.itemDoubleClicked.connect(self.show_diff)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.setColumnWidth(0, 300) # 30% of original 330 container width
        tree_container_layout.addWidget(self.tree)
        
        self.results_splitter.addWidget(tree_container)
        
        self.script_view = QTextEdit()
        self.script_view.setReadOnly(True)
        self.script_view.setPlaceholderText("Generated SQL script will appear here...")
        self.results_splitter.addWidget(self.script_view)
        
        # Start with script view hidden (100% tree)
        self.results_splitter.setSizes([1, 0])
        # Set stretch factors so they resize proportionally (3:7 ratio)
        self.results_splitter.setStretchFactor(0, 31)
        self.results_splitter.setStretchFactor(1, 69)
        
        main_layout.addWidget(self.results_splitter, stretch=1)
        
        self.statusBar().showMessage("Ready")

    def toggle_date_filter(self, state):
        self.date_edit.setEnabled(state == 2) # 2 is Checked

    def open_connection_dialog(self, connector, label_widget):
        dlg = ConnectionDialog(self)
        if dlg.exec():
            details = dlg.get_details()
            try:
                connector.connect(
                    details['server'], 
                    details['database'], 
                    details['username'], 
                    details['password'], 
                    details['trusted'],
                    details.get('trust_cert', False)
                )
                label_widget.setText(f"Connected to {details['database']} on {details['server']}")
                label_widget.setStyleSheet("color: green")
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))
                label_widget.setText("Connection Failed")
                label_widget.setStyleSheet("color: red")

    def load_object_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Object List", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.object_filter = {line.strip() for line in f if line.strip()}
                self.statusBar().showMessage(f"Loaded {len(self.object_filter)} objects from list")
                self.btn_clear_list.setEnabled(True)
                QMessageBox.information(self, "Success", f"Loaded {len(self.object_filter)} objects. Comparison will be restricted to these items.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def clear_object_list(self):
        self.object_filter = None
        self.btn_clear_list.setEnabled(False)
        self.statusBar().showMessage("Object list cleared. Next comparison will include all objects.")

    def run_comparison(self):
        if not self.source_connector.connection or not self.target_connector.connection:
            QMessageBox.warning(self, "Warning", "Please connect to both Source and Target databases.")
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.btn_compare.setEnabled(False)
            
            self.statusBar().showMessage("Extracting schemas...")
            QApplication.processEvents() # Force UI update
            
            source_extractor = SchemaExtractor(self.source_connector)
            target_extractor = SchemaExtractor(self.target_connector)
            
            self.source_schema = source_extractor.get_full_schema()
            self.target_schema = target_extractor.get_full_schema()
            
            # Apply file filter if exists
            if self.object_filter:
                self.source_schema = self._apply_object_filter(self.source_schema)
                self.target_schema = self._apply_object_filter(self.target_schema)

            self.statusBar().showMessage("Comparing...")
            QApplication.processEvents() # Force UI update

            comparer = SchemaComparer()
            self.diff = comparer.compare(self.source_schema, self.target_schema)

            # Apply date filter if enabled
            if self.chk_date_filter.isChecked():
                filter_date_q = self.date_edit.date()
                filter_dt = datetime(filter_date_q.year(), filter_date_q.month(), filter_date_q.day())
                self.diff = self._apply_date_filter(self.diff, filter_dt)
            
            self._populate_tree(self.diff)
            self.btn_generate.setEnabled(True)
            self.btn_save_comp.setEnabled(True)
            self.statusBar().showMessage("Comparison Complete")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Comparison failed: {str(e)}")
            self.statusBar().showMessage("Error during comparison")
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_compare.setEnabled(True)

    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item or item.parent() is None: # Not an object
            return
            
        # Only show for objects, not categories like "New" or "Tables"
        if item.childCount() > 0 and item.text(1) == "":
            return

        menu = QMenu()
        diff_action = menu.addAction("Show Comparison")
        diff_action.triggered.connect(lambda: self.show_diff(item))
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def save_comparison(self):
        if not self.diff:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Comparison", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                data = {
                    "saved_at": datetime.now().isoformat(),
                    "diff": self.diff,
                    "source_schema": self.source_schema,
                    "target_schema": self.target_schema
                }
                def json_serial(obj):
                    """JSON serializer for objects not serializable by default json code"""
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4, default=json_serial)
                self.statusBar().showMessage(f"Comparison saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save comparison: {str(e)}")

    def load_comparison(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Comparison", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                self.diff = data.get("diff")
                self.source_schema = data.get("source_schema")
                self.target_schema = data.get("target_schema")
                
                if not self.diff or not self.source_schema or not self.target_schema:
                    raise ValueError("Invalid comparison file format.")
                
                self._populate_tree(self.diff)
                self.btn_generate.setEnabled(True)
                self.btn_save_comp.setEnabled(True)
                self.statusBar().showMessage(f"Loaded comparison from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load comparison: {str(e)}")

    def show_diff(self, item, column=0):
        # Determine object name and type
        obj_name = item.text(0)
        
        # Traverse up to find the category (Tables, Procedures, etc.)
        p = item.parent()
        if not p: return
        
        # If double clicked a child (like a column), go up to the object
        if p.parent() and p.parent().parent():
             item = p
             obj_name = item.text(0)
             p = item.parent()
             
        # Now p is "New", "Modified", or "Dropped"
        if not p.parent(): return
        category = p.parent().text(0).lower()
        
        src_def = None
        tgt_def = None
        
        if category in self.source_schema:
            src_def = self.source_schema[category].get(obj_name)
        if category in self.target_schema:
            tgt_def = self.target_schema[category].get(obj_name)
            
        if src_def or tgt_def:
            dlg = DiffDialog(obj_name, src_def, tgt_def, self)
            dlg.exec()

    def _apply_object_filter(self, schema):
        """Restricts the schema to only include objects present in self.object_filter."""
        filtered_schema = {}
        for obj_type in ['tables', 'procedures', 'functions', 'triggers']:
            filtered_schema[obj_type] = {
                name: details for name, details in schema[obj_type].items() 
                if name in self.object_filter
            }
        return filtered_schema

    def _apply_date_filter(self, diff, cutoff_date):
        """Filters the diff to include only objects modified on or after cutoff_date.
           Note: Dropped objects are filtered out because they don't exist in source to have a date."""
        filtered_diff = {
            'tables': {'new': {}, 'modified': {}, 'dropped': []},
            'procedures': {'new': {}, 'modified': {}, 'dropped': []},
            'functions': {'new': {}, 'modified': {}, 'dropped': []},
            'triggers': {'new': {}, 'modified': {}, 'dropped': []}
        }

        for category in ['tables', 'procedures', 'functions', 'triggers']:
            # 1. New Objects
            for name, details in diff[category]['new'].items():
                # For new objects, the details ARE the schema definition from source
                # schema.py puts modify_date in the definition
                obj_date = details.get('modify_date') 
                if obj_date and obj_date >= cutoff_date:
                    filtered_diff[category]['new'][name] = details

            # 2. Modified Objects
            for name, changes in diff[category]['modified'].items():
                # For modified objects, we look up the object in self.source_schema to find its date
                source_obj = self.source_schema[category].get(name)
                if source_obj:
                    obj_date = source_obj.get('modify_date')
                    if obj_date and obj_date >= cutoff_date:
                        filtered_diff[category]['modified'][name] = changes

            # 3. Dropped Objects - INCLUDED
            # Dropped objects are only in Target, so "Source Date" filter doesn't apply to them.
            # We include them so the user sees all changes except those EXPLICITLY filtered out by source date.
            if diff[category]['dropped']:
                filtered_diff[category]['dropped'] = list(diff[category]['dropped'])
            
        return filtered_diff

    def _populate_tree(self, diff):
        self.tree.itemChanged.disconnect(self._handle_tree_check) if hasattr(self, '_handle_tree_check_connected') else None
        self.tree.clear()
        
        for section in ['tables', 'procedures', 'functions', 'triggers']:
            section_diff = diff[section]
            
            if not section_diff['new'] and not section_diff['modified'] and not section_diff['dropped']:
                continue
                
            root = QTreeWidgetItem(self.tree, [section.capitalize(), "", ""])
            root.setCheckState(0, Qt.CheckState.Checked)
            
            # New
            if section_diff['new']:
                new_root = QTreeWidgetItem(root, ["New", "", ""])
                new_root.setCheckState(0, Qt.CheckState.Checked)
                for name in section_diff['new']:
                    item = QTreeWidgetItem(new_root, [name, "Create", ""])
                    item.setCheckState(0, Qt.CheckState.Checked)
            
            # Modified
            if section_diff['modified']:
                mod_root = QTreeWidgetItem(root, ["Modified", "", ""])
                mod_root.setCheckState(0, Qt.CheckState.Checked)
                for name, changes in section_diff['modified'].items():
                    obj_node = QTreeWidgetItem(mod_root, [name, "Alter/Modify", ""])
                    obj_node.setCheckState(0, Qt.CheckState.Checked)
                    if section == 'tables':
                        for col_name in changes['add_columns']:
                            QTreeWidgetItem(obj_node, [col_name, "Add Column", ""])
                        for col_name in changes['alter_columns']:
                             QTreeWidgetItem(obj_node, [col_name, "Alter Column", "Mismatch"])
                        for col_name in changes['drop_columns']:
                            QTreeWidgetItem(obj_node, [col_name, "Drop Column", ""])
            
            # Dropped
            if section_diff['dropped']:
                drop_root = QTreeWidgetItem(root, ["Dropped (Target only)", "", ""])
                drop_root.setCheckState(0, Qt.CheckState.Checked)
                for name in section_diff['dropped']:
                    item = QTreeWidgetItem(drop_root, [name, "Drop", ""])
                    item.setCheckState(0, Qt.CheckState.Checked)
                
        self.tree.collapseAll()
        self.tree.itemChanged.connect(self._handle_tree_check)
        self._handle_tree_check_connected = True
        self.search_input.clear() # Clear search when data changes

    def filter_tree(self, text):
        """Filters the tree view based on the search text."""
        text = text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            root_item = self.tree.topLevelItem(i)
            self._filter_item(root_item, text)

    def _filter_item(self, item, text):
        """Recursively checks if item or any of its children matches text."""
        match = text in item.text(0).lower()
        
        any_child_match = False
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), text):
                any_child_match = True
        
        should_be_visible = match or any_child_match
        item.setHidden(not should_be_visible)
        
        # Expand item if a child matches to show it
        if any_child_match and text != "":
            item.setExpanded(True)
            
        return should_be_visible

    def _handle_tree_check(self, item, column):
        """Recursively check/uncheck children if a parent is toggled."""
        if column != 0:
            return
            
        state = item.checkState(0)
        self.tree.blockSignals(True)
        self._set_children_checkstate(item, state)
        self.tree.blockSignals(False)

    def _set_children_checkstate(self, item, state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._set_children_checkstate(child, state)

    def generate_script(self):
        if not self.diff:
            return
        
        try:
            selected_diff = self._get_selected_diff()
            generator = ScriptGenerator()
            sql = generator.generate(selected_diff)
            self.script_view.setText(sql)
            
            # Show the script view (30/70 split)
            self.results_splitter.setSizes([330, 770])
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Generation failed: {str(e)}")

    def _get_selected_diff(self):
        """Constructs a new diff object containing only checked items from the tree."""
        # Initialize as empty structure
        s_diff = {
            'tables': {'new': {}, 'modified': {}, 'dropped': []},
            'procedures': {'new': {}, 'modified': {}, 'dropped': []},
            'functions': {'new': {}, 'modified': {}, 'dropped': []},
            'triggers': {'new': {}, 'modified': {}, 'dropped': []}
        }
        
        # Traverse categories
        for i in range(self.tree.topLevelItemCount()):
            category_node = self.tree.topLevelItem(i)
            category_name = category_node.text(0).lower() # Tables, Procedures, etc.
            
            # Traverse segments (New, Modified, Dropped)
            for j in range(category_node.childCount()):
                segment_node = category_node.child(j)
                segment_name = segment_node.text(0).lower() # New, Modified, Dropped...
                
                # Traverse individual objects
                for k in range(segment_node.childCount()):
                    obj_node = segment_node.child(k)
                    if obj_node.checkState(0) == Qt.CheckState.Checked:
                        obj_name = obj_node.text(0)
                        
                        # Populate s_diff from self.diff
                        if "new" in segment_name:
                            s_diff[category_name]['new'][obj_name] = self.diff[category_name]['new'][obj_name]
                        elif "modified" in segment_name:
                            s_diff[category_name]['modified'][obj_name] = self.diff[category_name]['modified'][obj_name]
                        elif "dropped" in segment_name:
                            s_diff[category_name]['dropped'].append(obj_name)
                            
        return s_diff
