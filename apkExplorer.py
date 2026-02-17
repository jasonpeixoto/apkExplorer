import sys
import zipfile
import io
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QVBoxLayout, QHBoxLayout,
                             QWidget, QFileDialog, QPushButton, QMessageBox, QHeaderView,
                             QLineEdit, QMenu, QLabel, QCheckBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from PyQt5.QtCore import Qt


class DeepApkExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro APK Explorer - Jason Peixoto")
        self.main_zip_path = None

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['File Structure', 'Size'])

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.tree.setColumnWidth(1, 150)

        layout = QVBoxLayout()

        btn_open = QPushButton("SELECT MAIN ZIP FILE")
        btn_open.setStyleSheet("""
            QPushButton { background-color: #444; color: #00FF00; font-size: 18px; 
                          font-weight: bold; padding: 15px; border: 2px solid #00FF00; }
            QPushButton:hover { background-color: #555; }
        """)
        btn_open.clicked.connect(self.open_and_process_zip)

        self.path_label = QLabel("No file selected")
        self.path_label.setStyleSheet("color: #AAAAAA; font-style: italic; padding: 5px;")

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search multiple files (space separated)...")
        self.search_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #555;")
        self.search_input.textChanged.connect(self.search_and_highlight)

        self.filter_checkbox = QCheckBox("Show Matches Only")
        self.filter_checkbox.setStyleSheet("color: white; padding-left: 10px;")
        self.filter_checkbox.stateChanged.connect(self.search_and_highlight)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_checkbox)

        layout.addWidget(btn_open)
        layout.addWidget(self.path_label)
        layout.addLayout(search_layout)
        layout.addWidget(self.tree)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.showMaximized()

    def resizeEvent(self, event):
        if hasattr(self, 'tree') and self.tree.width() > 100:
            self.tree.setColumnWidth(0, int(self.tree.width() * 0.9))
        super().resizeEvent(event)

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
                    parent_item = QStandardItem(file_info.filename)
                    size_item = QStandardItem(f"{file_info.file_size:,} bytes")
                    parent_item.setData(("apk", file_info.filename, None), Qt.UserRole)

                    if file_info.filename.lower().endswith('.apk'):
                        parent_item.setForeground(QColor("#90EE90"))
                        self.expand_apk_contents(main_z, file_info.filename, parent_item)

                    self.model.appendRow([parent_item, size_item])
            self.tree.expandAll()
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
                        child_name = QStandardItem(f"  └─ {info.filename}")
                        child_size = QStandardItem(f"{info.file_size:,} bytes")
                        child_name.setForeground(QColor("#00FFFF"))
                        child_name.setData(("file", info.filename, apk_name), Qt.UserRole)
                        parent_node.appendRow([child_name, child_size])
        except:
            parent_node.appendRow([QStandardItem("[Unreadable]"), QStandardItem("-")])

    def search_and_highlight(self):
        raw_query = self.search_input.text().lower()
        queries = [q.strip() for q in raw_query.split(" ") if q.strip()]

        hide_unmatched = self.filter_checkbox.isChecked()
        highlight_brush = QBrush(QColor("#D35400"))

        self.tree.setUpdatesEnabled(False)
        self.first_match_index = None  # Reset for auto-scroll

        for i in range(self.model.rowCount()):
            self._recursive_search(self.model.item(i), queries, highlight_brush, hide_unmatched)

        if self.first_match_index and queries:
            self.tree.scrollTo(self.first_match_index)

        self.tree.setUpdatesEnabled(True)

    def _recursive_search(self, item, queries, brush, hide_unmatched):
        item_text = item.text().lower()

        is_match = False
        if not queries:
            is_match = True
        else:
            for q in queries:
                if q in item_text:
                    is_match = True
                    break

        item.setBackground(brush if (is_match and queries) else Qt.transparent)

        # Track the very first match found in the whole tree
        if is_match and queries and self.first_match_index is None:
            self.first_match_index = item.index()

        any_child_matched = False
        for i in range(item.rowCount()):
            if self._recursive_search(item.child(i), queries, brush, hide_unmatched):
                any_child_matched = True

        should_be_visible = is_match or any_child_matched
        parent_idx = item.parent().index() if item.parent() else self.tree.rootIndex()

        if hide_unmatched and queries:
            self.tree.setRowHidden(item.row(), parent_idx, not should_be_visible)
        else:
            self.tree.setRowHidden(item.row(), parent_idx, False)

        return should_be_visible

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid(): return
        item = self.model.itemFromIndex(index)
        data = item.data(Qt.UserRole)
        if not data: return

        item_type, internal_path, parent_apk = data
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #333; color: white; }")

        if item_type == "apk":
            act = menu.addAction("Extract and Unzip APK content...")
            res = menu.exec_(self.tree.viewport().mapToGlobal(position))
            if res == act: self.extract_and_unzip_apk(internal_path)
        else:
            act = menu.addAction(f"Extract this file only...")
            res = menu.exec_(self.tree.viewport().mapToGlobal(position))
            if res == act: self.extract_single_file(parent_apk, internal_path)

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
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File As", os.path.basename(file_path))
        if not save_path: return
        try:
            with zipfile.ZipFile(self.main_zip_path, 'r') as z:
                with z.open(apk_path) as apk_file:
                    apk_data = io.BytesIO(apk_file.read())
                    with zipfile.ZipFile(apk_data) as inner_z:
                        with inner_z.open(file_path) as source, open(save_path, 'wb') as target:
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