# APK Deep Explorer 🔍

**Author:** Jason Peixoto  
**License:** Open Source

APK Deep Explorer is a high-performance Python-based GUI tool built with **PyQt5**. It is designed for developers and security researchers who need to peek inside ZIP archives containing multiple APK files without the hassle of manual extraction or renaming files.

## 🌟 Key Features

* **Nested Inspection:** View files inside APKs that are themselves inside a ZIP file—all in-memory without disk bloat.
* **Instant Path Display:** A dedicated path label shows the full source location of your active ZIP file.
* **Live Multi-Term Search:** Search for multiple keywords at once (e.g., manifest png xml) with real-time Orange highlighting.
* **Smart Filtering:** A "Show Matches Only" toggle that instantly hides all files and APKs that don't match your search terms.
* **Auto-Scroll Focus:** The UI automatically "snaps" and scrolls to the first match found as you type or filter.
* **High-Contrast Dark Mode:** Neon Green (APKs) and Electric Cyan (Internal files) coding for maximum readability on dark backgrounds.
* **Smart Extraction:**
    * **Full Extract & Unzip:** Right-click an APK to extract and automatically unzip its entire contents into a new folder.
    * **Targeted Extract:** Right-click a specific inner file to extract just that one asset.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
This project relies on PyQt5. You can install it using:
pip install PyQt5

---

## 🚀 How to Run

1. Clone or download the repository.
2. Navigate to the directory in your terminal:
   cd /Users/jpeixoto/PythonProjects/apkExplorer/
3. Launch the application:
   python3 apkExplorer.py

---

## 📖 Usage & Examples

### 1. Source Tracking
Once a file is loaded, the path is displayed clearly under the main button. This ensures you always know which version of a ZIP you are analyzing.

### 2. Instant Live Filtering
Check the Show Matches Only box and start typing. The tree will live-update, hiding everything except your specific targets.
* Example: Typing "icon" will hide all non-image folders, leaving only icon assets visible.

### 3. Space-Separated Search
Need to find different types of files at once? Just use a space.
* Example: Typing "classes.dex resources.arsc" will highlight both file types across every APK in the archive.

### 4. Automatic "Snap-to-Result"
As you refine your search, the explorer automatically scrolls to the first match it finds, eliminating the need to hunt through thousands of lines manually.

---

## 🤝 Contributing
This is an open-source project. Contributions, issues, and feature requests are welcome!

**Maintained by:** Jason Peixoto