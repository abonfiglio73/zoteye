---
layout: default
---

## What is ZotEye?

ZotEye is a free, open-source Python-based tool for Windows. It compares a document with the documents in the local [**Zotero**](https://www.zotero.org/) reference library, automatically identifying similar text and overlaps. It helps authors avoid article rejections due to potential plagiarism and assists editors in verifying the originality of submitted manuscripts. The ultimate goal is to enhance transparency and reliability in scientific research.

![Zoteye interface screenshot]({{ '/assets/images/zoteye-screenshot-interface.png' | relative_url }}){: .screenshot }
<br>*Screenshot of ZotEye graphical interface*<br><br>

## Who is ZotEye for?

- Researchers and PhD students
- Journal editors and reviewers
- Academic institutions
- Authors using Zotero for reference management

## Key Features

* 🚀 Graphical interface
* 🌎 Multilingual (EN, IT)
* 📚 PDF text extraction
* 🔍 Automatic similarity analysis between a document and the local Zotero reference library
* 🔪 Possibility of excluding sections (e.g., "references") and quoted sentences from analysis
* 🧠 NLP based on n‑grams (words)
* 🔢 Calculation of similarity percentages per document
* 🧾 Similarity report
* 💾 Local cache to speed up subsequent analyses
* 📅 Automatic updates

## Use Cases

- Prevent manuscript rejection due to potential plagiarism
- Verify originality of submitted manuscripts
- Generate similarity reports using only local data
- Ensure transparency and reliability in scientific research

## Technology Stack

- Windows 11 (64-bit)
- [Python](https://www.python.org/downloads/) framework (Python 3.11+)
- [Zotero](https://www.zotero.org/) for managing references and citations

## Installation Notes

The latest release can be downloaded from [here](https://github.com/abonfiglio73/zoteye/releases/latest). During installation, Python (if not present) and the necessary libraries will be downloaded and installed.
Please note that some browsers or security systems may show **warnings** when downloading or opening the installer: 
* In MS Edge, you might see: "_ZotEye_Installer.exe is not commonly downloaded. Make sure it is safe before opening it._" Click the three dots in the top-right corner and select Keep, then click the three dots in the bottom-right corner of the next window and select Keep Anyway.
* Tools such as Microsoft Defender SmartScreen may also block the installer. Right-click the file, choose Properties, click Unblock, and then OK. Once unblocked, the installer can be run normally.

## License

Zoteye is released as open-source software under the [MIT license](https://github.com/abonfiglio73/zoteye?tab=MIT-1-ov-file)
