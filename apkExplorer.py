import sys
import zipfile
import io
import os
import shutil
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QVBoxLayout, QHBoxLayout,
                             QWidget, QFileDialog, QPushButton, QMessageBox, QHeaderView,
                             QLineEdit, QMenu, QLabel, QCheckBox, QDialog, QTextEdit, QScrollArea)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QPixmap, QImage
from PyQt5.QtCore import Qt


class PreviewDialog(QDialog):
    def __init__(self, name, content, is_image=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview: {name}")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")

        if is_image:
            scroll = QScrollArea()
            label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(content)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            scroll.setWidget(label)
            scroll.setWidgetResizable(True)
            layout.addWidget(scroll)
        else:
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            try:
                text_edit.setPlainText(content.decode('utf-8', errors='replace'))
            except:
                text_edit.setPlainText("[Binary Content - Cannot Preview]")
            text_edit.setStyleSheet("font-family: 'Consolas', monospace; font-size: 13px; border: none;")
            layout.addWidget(text_edit)


class DeepApkExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro APK Explorer - Jason Peixoto")
        self.main_zip_path = None
        self.highlight_color = "#D35400"

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['File Structure', 'Size'])

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        # DOUBLE CLICK TRIGGER
        self.tree.doubleClicked.connect(self.on_double_click)

        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Fixed)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        btn_open = QPushButton("SELECT MAIN ZIP FILE")
        btn_open.setStyleSheet("""
            QPushButton { background-color: #444; color: #00FF00; font-size: 18px; 
                          font-weight: bold; padding: 15px; border: 2px solid #00FF00; }
            QPushButton:hover { background-color: #555; }
        """)
        btn_open.clicked.connect(self.open_and_process_zip)

        self.path_label = QLabel("No file selected")
        self.path_label.setStyleSheet("color: #AAAAAA; font-style: italic; padding: 2px 5px;")

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search (Regex or space-separated terms)...")
        self.search_input.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 1px solid #555; background: #222; color: white;")
        self.search_input.textChanged.connect(self.search_and_highlight)

        self.regex_checkbox = QCheckBox("Regex")
        self.regex_checkbox.setStyleSheet("color: #00FFFF; font-weight: bold;")
        self.regex_checkbox.stateChanged.connect(self.search_and_highlight)

        self.filter_checkbox = QCheckBox("Matches Only")
        self.filter_checkbox.setStyleSheet("color: white; font-weight: bold;")
        self.filter_checkbox.stateChanged.connect(self.search_and_highlight)

        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.regex_checkbox)
        search_layout.addWidget(self.filter_checkbox)

        main_layout.addWidget(btn_open)
        main_layout.addWidget(self.path_label)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.tree)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        total_width = self.tree.viewport().width()
        if total_width > 100:
            self.tree.setColumnWidth(0, int(total_width * 0.9))
            self.tree.setColumnWidth(1, total_width - int(total_width * 0.9))

    def create_item(self, text):
        item = QStandardItem(text)
        item.setEditable(False)  # GRID LOCK: NO EDITING
        return item

    def open_and_process_zip(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Zip", "", "Zip Files (*.zip)")
        if not path: return
        self.main_zip_path = path
        self.path_label.setText(f"Source: {path}")
        self.model.removeRows(0, self.model.rowCount())
        self.tree.setUpdatesEnabled(False)

        try:
            with zipfile.ZipFile(path, 'r') as main_z:
                for file_info in main_z.infolist():
                    parent_item = self.create_item(file_info.filename)
                    size_item = self.create_item(f"{file_info.file_size:,} bytes")
                    parent_item.setData(("apk", file_info.filename, None), Qt.UserRole)

                    if file_info.filename.lower().endswith('.apk'):
                        parent_item.setForeground(QColor("#90EE90"))
                        self.expand_apk_contents(main_z, file_info.filename, parent_item)

                    self.model.appendRow([parent_item, size_item])
            self.tree.expandAll()
            if self.search_input.text():
                self.search_and_highlight()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.tree.setUpdatesEnabled(True)

    def expand_apk_contents(self, main_zip, apk_name, parent_node):
        try:
            with main_zip.open(apk_name) as apk_file:
                apk_data = io.BytesIO(apk_file.read())
                with zipfile.ZipFile(apk_data) as apk_z:
                    for info in apk_z.infolist():
                        child_name = self.create_item(f"  └─ {info.filename}")
                        child_size = self.create_item(f"{info.file_size:,} bytes")
                        child_name.setForeground(QColor("#00FFFF"))
                        child_name.setData(("file", info.filename, apk_name), Qt.UserRole)
                        parent_node.appendRow([child_name, child_size])
        except:
            parent_node.appendRow([self.create_item("[Unreadable]"), self.create_item("-")])

    def on_double_click(self, index):
        item = self.model.itemFromIndex(index)
        data = item.data(Qt.UserRole)
        if not data or data[0] != "file": return

        item_type, internal_path, parent_apk = data
        clean_path = internal_path.replace("  └─ ", "").strip()

        try:
            with zipfile.ZipFile(self.main_zip_path, 'r') as z:
                with z.open(parent_apk) as apk_file:
                    apk_data = io.BytesIO(apk_file.read())
                    with zipfile.ZipFile(apk_data) as inner_z:
                        with inner_z.open(clean_path) as target:
                            content = target.read()
                            is_img = clean_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp'))
                            prev = PreviewDialog(clean_path, content, is_img, self)
                            prev.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not open file: {e}")

    def search_and_highlight(self):
        raw_input = self.search_input.text()
        use_regex = self.regex_checkbox.isChecked()
        hide_unmatched = self.filter_checkbox.isChecked()
        highlight_brush = QBrush(QColor(self.highlight_color))

        self.search_input.setStyleSheet(
            "padding: 8px; font-size: 14px; border: 1px solid #555; background: #222; color: white;")
        raw_queries = [q.strip() for q in raw_input.split(" ") if q.strip()]
        compiled_patterns = []

        if raw_queries:
            try:
                for q in raw_queries:
                    pattern = q if use_regex else re.escape(q)
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                self.search_input.setStyleSheet("padding: 8px; border: 2px solid red; background: #222; color: white;")
                return

        self.tree.setUpdatesEnabled(False)
        self.first_match_index = None
        for i in range(self.model.rowCount()):
            self._recursive_search(self.model.item(i), compiled_patterns, highlight_brush, hide_unmatched)
        if self.first_match_index and raw_input:
            self.tree.scrollTo(self.first_match_index)
        self.tree.setUpdatesEnabled(True)

    def _recursive_search(self, item, patterns, brush, hide_unmatched):
        item_text = item.text()
        is_match = False
        if not patterns:
            is_match = True
        else:
            for p in patterns:
                if p.search(item_text):
                    is_match = True
                    break

        item.setBackground(brush if (is_match and patterns) else Qt.transparent)
        if is_match and patterns and self.first_match_index is None:
            self.first_match_index = item.index()

        any_child_matched = False
        for i in range(item.rowCount()):
            if self._recursive_search(item.child(i), patterns, brush, hide_unmatched):
                any_child_matched = True

        should_be_visible = is_match or any_child_matched
        parent_idx = item.parent().index() if item.parent() else self.tree.rootIndex()

        if hide_unmatched and patterns:
            self.tree.setRowHidden(item.row(), parent_idx, not should_be_visible)
        else:
            self.tree.setRowHidden(item.row(), parent_idx, False)
        return should_be_visible

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #333; color: white; }")
        extract_all_act = menu.addAction("⚡ Extract ALL Highlighted Files (Maintain Folders)")

        item_act = None
        if index.isValid():
            menu.addSeparator()
            item = self.model.itemFromIndex(index)
            data = item.data(Qt.UserRole)
            if data:
                item_type, internal_path, parent_apk = data
                item_act = menu.addAction(f"Extract this {'APK' if item_type == 'apk' else 'File'} only...")

        res = menu.exec_(self.tree.viewport().mapToGlobal(position))
        if res == extract_all_act:
            self.bulk_extract_highlighted()
        elif res == item_act and index.isValid():
            item_type, internal_path, parent_apk = data
            if item_type == "apk":
                self.extract_and_unzip_apk(internal_path)
            else:
                self.extract_single_file(parent_apk, internal_path)

    def bulk_extract_highlighted(self):
        dest_base = QFileDialog.getExistingDirectory(self, "Select Bulk Extraction Folder")
        if not dest_base: return
        highlighted_files = []
        for i in range(self.model.rowCount()):
            self._find_highlighted_recursive(self.model.item(i), highlighted_files)

        if not highlighted_files: return

        try:
            with zipfile.ZipFile(self.main_zip_path, 'r') as main_z:
                apk_groups = {}
                for apk, path in highlighted_files:
                    if apk not in apk_groups: apk_groups[apk] = []
                    apk_groups[apk].append(path)

                for apk_name, files in apk_groups.items():
                    with main_z.open(apk_name) as apk_file:
                        apk_data = io.BytesIO(apk_file.read())
                        with zipfile.ZipFile(apk_data) as inner_z:
                            for f_path in files:
                                clean_path = f_path.replace("  └─ ", "").strip()
                                out_path = os.path.join(dest_base, os.path.splitext(apk_name)[0], clean_path)
                                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                                with inner_z.open(clean_path) as source, open(out_path, 'wb') as target:
                                    shutil.copyfileobj(source, target)
            QMessageBox.information(self, "Success", f"Extracted {len(highlighted_files)} files.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _find_highlighted_recursive(self, item, result_list):
        data = item.data(Qt.UserRole)
        if data and data[0] == "file" and item.background().color().name().upper() == self.highlight_color.upper():
            result_list.append((data[2], data[1]))
        for i in range(item.rowCount()):
            self._find_highlighted_recursive(item.child(i), result_list)

    def extract_and_unzip_apk(self, apk_path):
        dest_base = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_base: return
        try:
            folder_name = os.path.splitext(os.path.basename(apk_path))[0]
            final_dir = os.path.join(dest_base, folder_name)
            os.makedirs(final_dir, exist_ok=True)
            with zipfile.ZipFile(self.main_zip_path, 'r') as z:
                with z.open(apk_path) as apk_file:
                    apk_data = io.BytesIO(apk_file.read())
                    with zipfile.ZipFile(apk_data) as inner_z:
                        inner_z.extractall(final_dir)
            QMessageBox.information(self, "Success", f"Unzipped to: {final_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def extract_single_file(self, apk_path, file_path):
        clean_path = file_path.replace("  └─ ", "").strip()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File As", os.path.basename(clean_path))
        if not save_path: return
        try:
            with zipfile.ZipFile(self.main_zip_path, 'r') as z:
                with z.open(apk_path) as apk_file:
                    apk_data = io.BytesIO(apk_file.read())
                    with zipfile.ZipFile(apk_data) as inner_z:
                        with inner_z.open(clean_path) as source, open(save_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            QMessageBox.information(self, "Success", "File extracted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DeepApkExplorer()
    window.show()
    sys.exit(app.exec_())