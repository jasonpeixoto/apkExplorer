# APK Deep Explorer 🔍

**Author:** Jason Peixoto  
**License:** Open Source

APK Deep Explorer is a high-performance Python-based GUI tool built with **PyQt5**. It is designed for developers and security researchers who need to peek inside ZIP archives containing multiple APK files without the hassle of manual extraction or renaming files.



## 🌟 Key Features

* **Nested Inspection:** View files inside APKs that are themselves inside a ZIP file—all in-memory without disk bloat.
* **Sticky Search on Load:** If you have a search query active, it automatically filters any new ZIP file you load immediately.
* **Multi-Regex & Live Search:** Treat each space-separated term as an independent Regex pattern with real-time Orange highlighting.
* **Smart Filtering:** A "Matches Only" toggle that instantly hides all files and APKs that don't match your search terms.
* **Bulk Structured Extraction:** Extract all highlighted files at once while maintaining their original internal folder structures.
* **High-Contrast UI:** Neon Green (APKs) and Electric Cyan (Internal files) coding for maximum readability on dark backgrounds.
* **Full-Width Workspace:** Optimized 90/10 column ratio ensures the file structure remains the priority.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
This project relies on `PyQt5`. You can install it using:

`pip install PyQt5`

---

## 🚀 How to Run

1. Clone or download the repository.
2. Navigate to the directory in your terminal:
   `cd /Users/jpeixoto/PythonProjects/apkExplorer/`
3. Launch the application:
   `python3 apkExplorer.py`

---

## 📖 Power User Examples

### 1. Advanced Regex Filtering
Enable **Regex** and type `\.xml$ \.png$`. 
* **Result:** The explorer will instantly isolate every XML and PNG file across all APKs, hiding everything else.

### 2. Bulk Extraction (Maintaining Structure)
Need every icon from 10 different APKs?
1. Type `icon` or `\.png$` in the search bar.
2. Check **Matches Only**.
3. Right-click and select **"Extract ALL Highlighted Files"**.
* **Result:** All files are saved into folders named after their parent APKs, with their internal subfolders (e.g., `res/drawable/`) recreated exactly.



### 3. Automatic "Snap-to-Result"
As you refine your search, the explorer automatically scrolls to the first match it finds, eliminating the need to hunt through thousands of lines manually.

---

## 🤝 Contributing
This is an open-source project. Contributions, issues, and feature requests are welcome!

**Maintained by:** Jason Peixoto