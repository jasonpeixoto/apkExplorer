# APK Deep Explorer 🔍

**Author:** Jason Peixoto  
**License:** Open Source

APK Deep Explorer is a high-performance Python-based GUI tool built with **PyQt5**. It is designed for developers and security researchers who need to peek inside ZIP archives containing multiple APK files without the hassle of manual extraction or renaming files.



## 🌟 Key Features

* **Instant File Preview:** Double-click any file to open a high-speed preview window. Supports images (PNG, JPG, WebP, BMP) and text-based files (XML, Manifests, Code).
* **Locked File Grid:** The main tree view is strictly read-only, preventing accidental file renames or edits while browsing thousands of entries.
* **Nested Inspection:** View files inside APKs that are themselves inside a ZIP file—all in-memory without disk bloat.
* **Sticky Search on Load:** Search filters and Regex patterns persist automatically across different loaded ZIP files for faster auditing.
* **Multi-Regex & Live Search:** Treat each space-separated term as an independent Regex pattern with real-time Orange highlighting.
* **Bulk Structured Extraction:** Extract all highlighted files at once while maintaining their original internal folder structures.
* **Full-Width Workspace:** Optimized 90/10 column ratio ensures the file structure remains the priority.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
This project relies on PyQt5. You can install it using the command:
pip install PyQt5

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



---

## 🤝 Contributing
This is an open-source project. Contributions, issues, and feature requests are welcome!

**Maintained by:** Jason Peixoto