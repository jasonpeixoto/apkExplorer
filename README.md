# APK Deep Explorer 🔍

**Author:** Jason Peixoto  
**License:** Open Source

APK Deep Explorer is a high-performance Python-based GUI tool built with **PyQt5**. It is designed for developers and security researchers who need to peek inside ZIP archives containing multiple APK files without the hassle of manual extraction or renaming files.

A high-performance, lightweight static analysis tool for exploring Android APKs, ZIP archives, and DEX files. Built for security researchers and reverse engineers who need speed, clarity, and deep inspection capabilities without the overhead of a full IDE.

## 🌟 Key Features V1.00

* **Instant File Preview:** Double-click any file to open a high-speed preview window. Supports images (PNG, JPG, WebP, BMP) and text-based files (XML, Manifests, Code).
* **Locked File Grid:** The main tree view is strictly read-only, preventing accidental file renames or edits while browsing thousands of entries.
* **Nested Inspection:** View files inside APKs that are themselves inside a ZIP file—all in-memory without disk bloat.
* **Sticky Search on Load:** Search filters and Regex patterns persist automatically across different loaded ZIP files for faster auditing.
* **Multi-Regex & Live Search:** Treat each space-separated term as an independent Regex pattern with real-time Orange highlighting.
* **Bulk Structured Extraction:** Extract all highlighted files at once while maintaining their original internal folder structures.
* **Full-Width Workspace:** Optimized 90/10 column ratio ensures the file structure remains the priority.

## 🌟 Key Features V1.01
* **Dual-Tab Preview:** Double-click any file for immediate inspection.
    * [cite_start]**XML:** Decodes binary Android XML (Manifests/Layouts) into readable text[cite: 1].
    * [cite_start]**DEX:** Provides a Java Source tab using Androguard[cite: 1].
    * [cite_start]**Raw:** Always available for binary or text fallback[cite: 1].
* [cite_start]**Robust AXML Decoder:** Custom logic to handle modern, obfuscated, or variable-length string pools in Android bundles[cite: 1].
* [cite_start]**Stability Fixes:** Includes global exception hooks and memory retention to prevent the app from "disappearing" on launch[cite: 1].
* **Locked File Grid:** Read-only tree view ensures data integrity during massive audits.
* [cite_start]**Full-Width Workspace:** Smart column stretching ensures the file structure remains the priority[cite: 1].

## 🌟 Key Features V1.02
### 🔍 Advanced Exploration & Navigation
* **Multi-Archive Support:** Load multiple APKs or ZIPs simultaneously into a unified Project Explorer.
* **Recursive Inspection:** Deep-dive into nested archives (APKs within ZIPs) with a simple double-click.
* **Smart Duplicate Prevention:** Automatically detects if an archive is already loaded to keep your workspace clean.
* **File Categorization:** Instant visual recognition with custom icons and color-coding:
    * 🟡 **DEX** (Dalvik Executable)
    * 🟠 **XML** (Manifests/Resources)
    * 🟢 **Archives** (APK/ZIP)
    * 🌿 **Images** (PNG/JPG/WebP)
    * ⚪ **Generic Files**

### 🛠️ Static Analysis Power Tools
* **AXML Decoder Pro:** Integrated binary XML decoder that resolves strings, attributes, and resource IDs into human-readable AndroidManifest.xml and layout files.
* **DEX Decompiler:** One-click decompilation of DEX files into Java source code using background threading to keep the UI snappy.
* **Disk-Based Caching:** Uses MD5 content hashing to cache decompiled Java files in `.dex_cache`. Once a file is decompiled, reopening it is instant.

### ⚡ Search & Filtering
* **Global String Search:** Scan every file in an archive for suspicious URLs, API keys, or logic strings with a dedicated results tab.
* **Power Filter:** Support for **Space-Separated Multi-Keyword** search (e.g., `xml dex main`) and **Regular Expressions** (Regex) to find exactly what you need in massive file trees.
* **Find in Tab (Ctrl+F):** Standard text searching within the current code viewer or manifest tab.

### 🎨 Modern UI/UX
* **Lazy Loading:** Optimized file tree rendering that prevents sluggishness even when loading massive 100MB+ APKs.
* **Syntax Highlighting:** Full Java syntax highlighting (Keywords, Strings, Comments) for decompiled code.
* **Preview Mode:** Single-click a file for an instant preview; double-click to lock it into a persistent tab.
* **Dynamic Layout:** Auto-stretching "Explorer" column with a compact "Size" column for maximum filename visibility.
---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
This project relies on PyQt5. You can install it using the command:
pip install PyQt5

   ```bash
   pip install PyQt5 androguard
   python apkExplorer.py
   ```

---

## 🚀 How to Run

1. Clone or download the repository.
2. Navigate to the directory in your terminal:
   cd /Users/jpeixoto/PythonProjects/apkExplorer/
3. Launch the application:
   python3 apkExplorer.py

---

## 📖 Power User Examples

### 1. Advanced Regex Filtering
Enable **Regex** and type: \.xml$ \.png$
* **Result:** The explorer isolates every XML and PNG file across all APKs instantly.

### 2. In-Memory Preview
Don't waste time extracting files just to see what they are. Simply **double-click** a .png to view the asset or an AndroidManifest.xml to read its content in a dark-themed text viewer.

### 3. Bulk Extraction (Maintaining Structure)
1. Search for a specific asset type (e.g., \.webp$).
2. Right-click anywhere and select **"Extract ALL Highlighted Files"**.
* **Result:** Files are saved into folders named after their parent APKs, with their internal subfolders recreated exactly (e.g., Output/BaseAPK/res/drawable/icon.webp).

## ⌨️ Shortcuts
| Shortcut | Action |
| :--- | :--- |
| **Ctrl + F** | Open "Find in Tab" search bar |
| **Double Click** | Open/Extract Archive or Open File Tab |
| **Right Click** | Remove Archive/File from Explorer |

---

## 🤝 Contributing
This is an open-source project. Contributions, issues, and feature requests are welcome!

**Maintained by:** Jason Peixoto
