import sys, zipfile, io, os, struct, hashlib, traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QVBoxLayout, QHBoxLayout,
                             QWidget, QFileDialog, QPushButton, QMessageBox, QHeaderView,
                             QLineEdit, QLabel, QTabWidget, QSplitter, QProgressBar,
                             QStyle, QTextEdit, QMenu, QFrame, QInputDialog)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QColor, QPixmap, QFont,
                         QSyntaxHighlighter, QTextCharFormat, QTextCursor)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRegularExpression

# --- CONFIG ---
CACHE_DIR = os.path.join(os.getcwd(), ".dex_cache")
if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)


# --- JAVA SYNTAX HIGHLIGHTER ---
class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []
        kw_fmt = QTextCharFormat();
        kw_fmt.setForeground(QColor("#569CD6"));
        kw_fmt.setFontWeight(QFont.Bold)
        keywords = ["public", "private", "protected", "static", "final", "void", "int", "class", "extends", "return",
                    "if", "else", "new", "import", "package"]
        for word in keywords: self.rules.append((QRegularExpression(f"\\b{word}\\b"), kw_fmt))
        str_fmt = QTextCharFormat();
        str_fmt.setForeground(QColor("#CE9178"))
        self.rules.append((QRegularExpression("\".*\""), str_fmt))
        com_fmt = QTextCharFormat();
        com_fmt.setForeground(QColor("#6A9955"))
        self.rules.append((QRegularExpression("//[^\n]*"), com_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next();
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


# --- AXML DECODER ---
class AXMLDecoder:
    def __init__(self, data):
        self.reader = io.BytesIO(data);
        self.strings = []

    def read_int(self):
        buf = self.reader.read(4);
        return struct.unpack('<I', buf)[0] if len(buf) == 4 else 0

    def read_short(self):
        buf = self.reader.read(2);
        return struct.unpack('<H', buf)[0] if len(buf) == 2 else 0

    def decode(self):
        try:
            self.reader.seek(0)
            if self.read_short() != 0x0003: return None
            self.read_short();
            f_sz = self.read_int();
            out = '<?xml version="1.0" encoding="utf-8"?>\n';
            indent = 0
            while self.reader.tell() < f_sz:
                pos = self.reader.tell();
                c_type = self.read_short();
                self.reader.read(2);
                c_sz = self.read_int()
                if c_type == 0x0001:
                    self.parse_strings(c_sz, pos)
                elif c_type == 0x0102:
                    self.reader.read(8);
                    ns_idx = self.read_int();
                    name_idx = self.read_int()
                    self.reader.read(4);
                    attr_count = self.read_short();
                    self.reader.read(6)
                    tag = self.get_s(name_idx);
                    out += "  " * indent + f"<{tag}"
                    for _ in range(attr_count):
                        self.reader.read(4);
                        a_nm_idx = self.read_int();
                        self.reader.read(4)
                        a_tp = ord(self.reader.read(1));
                        self.reader.read(3);
                        a_vl_raw = self.read_int()
                        a_nm = self.get_s(a_nm_idx);
                        a_vl = self.get_s(a_vl_raw) if (a_tp == 3 or a_vl_raw < len(self.strings)) else str(a_vl_raw)
                        out += f' {a_nm}="{a_vl}"'
                    out += ">\n";
                    indent += 1
                elif c_type == 0x0103:
                    indent = max(0, indent - 1);
                    self.reader.read(8);
                    self.reader.read(4)
                    out += "  " * indent + f"</{self.get_s(self.read_int())}>\n"
                self.reader.seek(pos + c_sz)
            return out
        except:
            return "[Parser Error]"

    def get_s(self, i):
        return self.strings[i] if 0 <= i < len(self.strings) else ""

    def parse_strings(self, size, pos):
        self.reader.seek(pos + 8);
        count = self.read_int();
        self.read_int();
        flags = self.read_int()
        str_start = self.read_int();
        self.read_int();
        offsets = [self.read_int() for _ in range(count)]
        is_utf8 = (flags & 0x100) != 0
        for off in offsets:
            self.reader.seek(pos + str_start + off)
            if is_utf8:
                u8_len = ord(self.reader.read(1))
                if u8_len & 0x80: u8_len = (u8_len & 0x7f) << 8 | ord(self.reader.read(1))
                self.strings.append(self.reader.read(u8_len).decode('utf-8', errors='ignore'))
            else:
                u16_len = self.read_short()
                if u16_len & 0x8000: u16_len = (u16_len & 0x7fff) << 16 | self.read_short()
                self.strings.append(self.reader.read(u16_len * 2).decode('utf-16le', errors='ignore'))


# --- WORKERS ---
class DecompileWorker(QThread):
    finished = pyqtSignal(str, str, bool)

    def __init__(self, filename, data, is_preview):
        super().__init__();
        self.filename = filename;
        self.data = data;
        self.is_preview = is_preview

    def run(self):
        h = hashlib.md5(self.data).hexdigest();
        cp = os.path.join(CACHE_DIR, f"{h}.java")
        if os.path.exists(cp):
            with open(cp, "r", encoding="utf-8") as f: self.finished.emit(self.filename, f.read(),
                                                                          self.is_preview); return
        try:
            from androguard.core.dex import DEX;
            from androguard.core.analysis.analysis import Analysis;
            from androguard.decompiler.decompile import DvMethod
            df = DEX(self.data);
            dx = Analysis(df);
            out = []
            for cls in df.get_classes()[:20]:
                for m in cls.get_methods():
                    mx = dx.get_method(m);
                    if mx: d = DvMethod(mx); d.process(); src = d.get_source();
                    if src: out.append(src)
            code = "\n".join(out);
            with open(cp, "w", encoding="utf-8") as f:
                f.write(code)
            self.finished.emit(self.filename, code, self.is_preview)
        except Exception as e:
            self.finished.emit(self.filename, f"// Error: {e}", self.is_preview)


class SearchWorker(QThread):
    match_found = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, data, query):
        super().__init__();
        self.data = data;
        self.query = query.lower()

    def run(self):
        try:
            with zipfile.ZipFile(io.BytesIO(self.data)) as z:
                for n in z.namelist():
                    if any(n.endswith(x) for x in ['.png', '.jpg', '.so']): continue
                    try:
                        raw = z.read(n)
                        content = AXMLDecoder(raw).decode() if n.endswith('.xml') else raw.decode('utf-8',
                                                                                                  errors='ignore')
                        if self.query in content.lower():
                            idx = content.lower().find(self.query)
                            snippet = content[max(0, idx - 20):min(len(content), idx + 40)].replace('\n', ' ')
                            self.match_found.emit(n, f"...{snippet}...")
                    except:
                        continue
        except:
            pass
        self.finished.emit()


# --- MAIN IDE ---
class ApkExplorerIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        # SET VERSION TITLE TO V1.02
        self.setWindowTitle("ApkExplorerIDE V1.02")
        self.resize(1400, 900);
        self.preview_tab_index = -1;
        self.init_ui();
        self.apply_style()

    def init_ui(self):
        central = QWidget();
        self.setCentralWidget(central);
        layout = QHBoxLayout(central);
        self.splitter = QSplitter(Qt.Horizontal)
        left_pane = QWidget();
        vbox = QVBoxLayout(left_pane)
        vbox.addWidget(QPushButton("📂 OPEN APK", clicked=self.open_archive))
        vbox.addWidget(QPushButton("🔍 GLOBAL SEARCH", clicked=self.start_global_search))
        self.filter = QLineEdit();
        self.filter.setPlaceholderText("Filter (Regex or 'word1 word2')...");
        self.filter.textChanged.connect(self.do_filter)
        vbox.addWidget(self.filter)

        self.tree = QTreeView();
        self.model = QStandardItemModel();
        self.model.setHorizontalHeaderLabels(['Explorer', 'Size'])
        self.tree.setModel(self.model);
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu);
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.clicked.connect(lambda i: self.handle_click(i, True));
        self.tree.doubleClicked.connect(lambda i: self.handle_click(i, False))
        h = self.tree.header();
        h.setStretchLastSection(False);
        h.setSectionResizeMode(0, QHeaderView.Stretch);
        h.setSectionResizeMode(1, QHeaderView.Fixed);
        h.setDefaultSectionSize(100)
        vbox.addWidget(self.tree)

        right_container = QWidget();
        right_vbox = QVBoxLayout(right_container)
        self.tabs = QTabWidget();
        self.tabs.setTabsClosable(True);
        self.tabs.tabCloseRequested.connect(self.close_tab);
        right_vbox.addWidget(self.tabs)
        self.find_bar = QFrame();
        self.find_bar.setVisible(False);
        find_layout = QHBoxLayout(self.find_bar)
        self.find_input = QLineEdit();
        self.find_input.setPlaceholderText("Find in current tab...");
        self.find_input.returnPressed.connect(self.find_next);
        find_layout.addWidget(self.find_input)
        btn_next = QPushButton("Next");
        btn_next.clicked.connect(self.find_next);
        find_layout.addWidget(btn_next)
        btn_close_find = QPushButton("X");
        btn_close_find.setFixedWidth(30);
        btn_close_find.clicked.connect(lambda: self.find_bar.setVisible(False));
        find_layout.addWidget(btn_close_find)
        right_vbox.addWidget(self.find_bar);
        self.splitter.addWidget(left_pane);
        self.splitter.addWidget(right_container);
        self.splitter.setStretchFactor(1, 4)
        layout.addWidget(self.splitter);
        self.progress = QProgressBar();
        self.progress.setVisible(False);
        self.statusBar().addPermanentWidget(self.progress)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #1E1E1E; color: #D4D4D4; } 
            QTreeView { background: #252526; border: none; font-size: 12px; } 
            QHeaderView::section { background: #333; color: #CCC; padding: 4px; border: 1px solid #111; } 
            QTabBar::tab { background: #2D2D2D; padding: 10px; border-right: 1px solid #111; } 
            QTabBar::tab:selected { background: #1E1E1E; border-bottom: 2px solid #007ACC; } 
            QPushButton { background: #333; border: 1px solid #555; padding: 8px; font-weight: bold; }
        """)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F: self.find_bar.setVisible(
            True); self.find_input.setFocus()
        super().keyPressEvent(event)

    def find_next(self):
        curr = self.tabs.currentWidget()
        if isinstance(curr, QTextEdit):
            if not curr.find(self.find_input.text()): curr.moveCursor(QTextCursor.Start); curr.find(
                self.find_input.text())

    def load_zip(self, name, data):
        dn = os.path.basename(name)
        for i in range(self.model.rowCount()):
            if self.model.item(i).text() == dn: self.tree.setCurrentIndex(self.model.index(i, 0)); self.tree.expand(
                self.model.index(i, 0)); return
        root = QStandardItem(dn);
        root.setData(data, Qt.UserRole);
        root.setIcon(QApplication.style().standardIcon(QStyle.SP_DriveHDIcon))
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for info in z.infolist():
                    ext = info.filename.lower();
                    s = QApplication.style();
                    icon, color = s.standardIcon(QStyle.SP_FileIcon), QColor("#D4D4D4")
                    if ext.endswith(('.apk', '.zip')):
                        icon, color = s.standardIcon(QStyle.SP_DirIcon), QColor("#4EC9B0")
                    elif ext.endswith('.dex'):
                        color = QColor("#FFD700")
                    elif ext.endswith('.xml'):
                        icon, color = s.standardIcon(QStyle.SP_FileLinkIcon), QColor("#CE9178")
                    elif ext.endswith(('.png', '.jpg')):
                        icon, color = s.standardIcon(QStyle.SP_FileDialogContentsView), QColor("#B5CEA8")
                    it = QStandardItem(icon, info.filename);
                    it.setForeground(color);
                    it.setData(data, Qt.UserRole + 1)
                    sz = QStandardItem(f"{info.file_size:,}");
                    sz.setForeground(QColor("#808080"));
                    root.appendRow([it, sz])
            self.model.appendRow(root);
            self.tree.expand(root.index());
            self.do_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_click(self, idx, is_preview):
        if idx.column() != 0: return
        it = self.model.itemFromIndex(idx);
        fn = it.text();
        pd = it.data(Qt.UserRole + 1)
        if not pd: return
        with zipfile.ZipFile(io.BytesIO(pd)) as z:
            raw = z.read(fn)
        if fn.lower().endswith(('.apk', '.zip')) and not is_preview: self.load_zip(fn, raw); return
        if fn.lower().endswith('.dex'):
            self.progress.setVisible(True);
            self.progress.setRange(0, 0);
            self.dw = DecompileWorker(fn, raw, is_preview);
            self.dw.finished.connect(self.add_tab);
            self.dw.start()
        elif fn.lower().endswith('.xml'):
            self.add_tab(fn, AXMLDecoder(raw).decode() or "[Error]", is_preview)
        elif fn.lower().endswith(('.png', '.jpg')):
            l = QLabel();
            p = QPixmap();
            p.loadFromData(raw);
            l.setPixmap(p.scaled(600, 600, Qt.KeepAspectRatio));
            l.setAlignment(Qt.AlignCenter);
            self.add_tab(fn, l, is_preview)
        else:
            try:
                txt = raw.decode('utf-8', errors='replace')
            except:
                txt = "[Binary]"
            self.add_tab(fn, txt, is_preview)

    def add_tab(self, fn, content, is_preview):
        self.progress.setVisible(False);
        v = QTextEdit() if isinstance(content, str) else content
        if isinstance(content, str): v.setReadOnly(True); v.setPlainText(content); v.setFont(QFont("Consolas", 10))
        if fn.lower().endswith('.dex') and isinstance(content, str): self.highlighter = JavaHighlighter(v.document())
        title = os.path.basename(fn)
        if is_preview:
            if self.preview_tab_index != -1: self.tabs.removeTab(self.preview_tab_index)
            self.preview_tab_index = self.tabs.insertTab(0, v, f"👁 {title}");
            self.tabs.setCurrentIndex(0)
        else:
            self.tabs.addTab(v, title); self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def start_global_search(self):
        # FIXED: QInputDialog used correctly here
        query, ok = QInputDialog.getText(self, "Global Search", "String:")
        if not ok or not query: return
        if self.model.rowCount() == 0: return

        res = QTextEdit();
        res.setReadOnly(True);
        self.tabs.addTab(res, f"🔍 {query}");
        self.progress.setVisible(True);
        self.progress.setRange(0, 0)
        self.sw = SearchWorker(self.model.item(0).data(Qt.UserRole), query)
        self.sw.match_found.connect(lambda f, s: res.append(f"<b>{f}</b>: {s}\n"));
        self.sw.finished.connect(lambda: self.progress.setVisible(False));
        self.sw.start()

    def do_filter(self):
        rt = self.filter.text().strip();
        rx = QRegularExpression(rt, QRegularExpression.CaseInsensitiveOption);
        kw = rt.lower().split(' ')
        for i in range(self.model.rowCount()):
            root = self.model.item(i);
            root_vis = False
            for j in range(root.rowCount()):
                fn = root.child(j).text().lower();
                m = any(k in fn for k in kw) or rx.match(fn).hasMatch()
                self.tree.setRowHidden(j, root.index(), not m if rt else False);
                root_vis = root_vis or m
            self.tree.setRowHidden(i, self.tree.rootIndex(), not root_vis if rt else False)

    def open_archive(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select APK", "", "Archives (*.apk *.zip)")
        if p:
            with open(p, 'rb') as f: self.load_zip(p, f.read())

    def show_context_menu(self, pos):
        idx = self.tree.indexAt(pos);
        if idx.isValid():
            menu = QMenu();
            remove_act = menu.addAction("Remove From Explorer")
            if menu.exec_(self.tree.mapToGlobal(pos)) == remove_act:
                item = self.model.itemFromIndex(idx)
                if item.parent():
                    item.parent().removeRow(item.row())
                else:
                    self.model.removeRow(item.row())

    def close_tab(self, i):
        if i == self.preview_tab_index: self.preview_tab_index = -1
        self.tabs.removeTab(i)


if __name__ == "__main__":
    app = QApplication(sys.argv);
    app.setStyle("Fusion");
    ide = ApkExplorerIDE();
    ide.show();
    sys.exit(app.exec_())
