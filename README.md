# APK Deep Explorer 🔍

**Author:** Jason Peixoto  
**License:** Open Source

APK Deep Explorer is a high-performance Python-based GUI tool built with **PyQt5**. It is designed for developers and security researchers who need to peek inside ZIP archives containing multiple APK files without the hassle of manual extraction or renaming files.

## 🌟 Key Features

* **Nested Inspection:** View files inside APKs that are themselves inside a ZIP file—all without extracting to disk.
* **In-Memory Processing:** Uses io.BytesIO to read nested archives in RAM for speed and security.
* **High-Contrast Dark Mode UI:** Features a neon color scheme (Cyan and Green) for perfect readability on dark backgrounds.
* **Deep Search:** Instantly scan every file across all nested APKs and highlight matches in Orange.
* **Smart Extraction:**
    * **Full Extract:** Right-click an APK to extract and automatically unzip its entire contents into a folder.
    * **Selective Extract:** Right-click a specific file inside an APK to pull just that one file out.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
This project relies on PyQt5. You can install it via pip:
pip install PyQt5

---

## 🚀 How to Run

1. Clone or download the repository.
2. Navigate to the directory in your terminal:
   cd apkExplorer/
3. Launch the application:
   python3 apkExplorer.py

---

## 📖 Usage Examples

### 1. Loading your Archive
Click the SELECT MAIN ZIP FILE button. Once selected, the program will automatically perform a deep-scan and expand all APK contents into a visual tree.

### 2. Finding Specific Files
Use the search bar at the top to find assets or manifest files.
* Example: Type classes.dex and hit Enter.
* Result: Every classes.dex in every APK will be highlighted in Orange.

### 3. Quick Extraction
* Scenario: You found a specific image in app_v1.apk and want it.
* Action: Right-click the file -> "Extract this file only" -> Choose your save location.

---

## 🤝 Contributing
This is an open-source project. Contributions, issues, and feature requests are welcome!

**Maintained by:** Jason Peixoto