<p align="center" style="margin: 0; padding: 0;">
  <img src="llamarker/assets/Llamarker_logo.png" alt="LlaMarker Logo" width="200">
</p>

<h1 align="center">🖍️ LlaMarker</h1>

<p align="center">
  <b>Your go-to tool for converting and parsing documents into clean, well-structured Markdown!</b><br>
  <i>Fast, intuitive, and entirely local 💻🚀.</i>
</p>

<div align="center">
  <span>
    <a href="https://www.python.org/downloads/release/python-380/">
      <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Versions">
    </a>
  </span>
  <span>
    <a href="https://github.com/VikParuchuri/marker">
      <img src="https://img.shields.io/badge/License-Refer%20Marker%20Repo-lightgrey.svg" alt="License">
    </a>
  </span>
  <span>
    <a href="https://pypi.org/project/llamarker/">
      <img src="https://img.shields.io/pypi/v/llamarker" alt="PyPI version">
    </a>
  </span>
</div>


<p align="center">
  <img src="llamarker/assets/llamarker_demo.gif" alt="LlaMarker Demo" width="1200">
</p>


## ✨ Key Features

- ✨ **All-in-One Parsing**  
  Supports **TXT**, **DOCX**, **PDF**, **PPT**, **XLSX**, and more—even processes images inside documents.

- 🖼️ **Visual Content Extraction**  
  Utilizes **Llama 3.2 Vision** to detect images, tables, charts, and diagrams, converting them into rich Markdown.

- 🏗️ **Built with Marker**  
  Extends the open-source [Marker](https://github.com/VikParuchuri/marker) parser to handle complex content types **locally**.

- 🛡️ **Local-First Privacy**  
  No cloud, no external servers—**all processing** happens on your machine.

---

## 🚀 How It Works

1. **Parsing & Conversion**

   - Parses and converts multiple file types (.txt, .docx, .pdf, .ppt, .xlsx, etc.) into Markdown.
   - Leverages **Marker** for accurate and efficient parsing of both text and visual elements.
   - Extracts images, charts, and tables, embedding them in Markdown.
   - _(Optional)_ Converts documents into PDFs using **LibreOffice** for easy viewing.

2. **Visual Analysis**

   - Distinguishes logos from content-rich images.
   - Extracts and preserves the original language from images.
   - Uses multiple agents to extract useful information from the images.

3. **Fast & Efficient**

   - Supports parallel processing for faster handling of large folders.

4. **Streamlit GUI**
   - A user-friendly interface to upload and parse files (or multiple files at once!) or entire directories.
   - Download results directly from the GUI.

---

## 📑 Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation Options](#installation-options)
   - [Install via PyPI](#install-via-pypi)
   - [Local Development Setup](#local-development-setup)
4. [Basic Usage](#basic-usage)
   - [CLI Usage](#cli-usage)
   - [Streamlit GUI](#streamlit-gui)
5. [Advanced Usage](#advanced-usage)
   - [Command-Line Arguments](#command-line-arguments)
   - [Example Commands](#example-commands)
6. [Output Structure](#output-structure)
7. [Code Example](#code-example)
8. [Contributing](#contributing)
9. [License](#license)
10. [Acknowledgments](#acknowledgments)

---

## ✨ Features

- 📄 **Document Conversion**  
  Converts `.txt`, `.docx`, and other supported file types into `.pdf` using **LibreOffice** (optional if you only need to parse PDFs).

- 📊 **Page Counting**  
  Automatically counts pages in PDFs using **PyPDF2**.

- 🖼️ **Image Processing**  
  Analyzes images to differentiate logos from content-rich images. Extracts relevant data and updates the corresponding Markdown file.

- ✍️ **Markdown Parsing**  
  Uses **Marker** to generate clean, structured Markdown files from parsed PDFs.

- 🌐 **Multilingual Support**  
  Maintains the original language of the content during extraction.

- 📈 **Data Visualization**  
  Generates analysis plots based on the page counts of processed documents.

---

## ⚙️ Prerequisites

Before installing or running **LlaMarker**, please ensure you meet the following requirements:

1. **Python 3.10+**

   - Core language for running **LlaMarker**.
   - Verify your Python version:
     ```bash
     python --version
     ```

2. **Marker**

   - [Marker](https://github.com/VikParuchuri/marker) is an open-source parser that **LlaMarker** extends.
   - For a quick install, you can try:
     ```bash
     pip install marker-pdf
     ```
     This installs Marker’s **PDF** parsing capabilities.
   - If you plan to leverage GPUs, ensure **PyTorch** is installed with **CUDA** support (e.g., via `pytorch-cuda` or the official PyTorch distribution).
   - For advanced installation or customization, refer to the [official Marker GitHub repository](https://github.com/VikParuchuri/marker) for detailed instructions on cloning and building from source.
   - If installed, ensure Marker is in your `PATH` or specify its location with the `--marker_path` argument.

3. **LibreOffice**

   - Required for converting `.docx`, `.ppt`, `.xlsx`, etc., into `.pdf` before parsing.
   - **Linux** (Ubuntu/Debian example):
     ```bash
     sudo apt update
     sudo apt install libreoffice
     ```
   - **Windows**:  
     [Download the installer](https://www.libreoffice.org/download/download/) and consider adding LibreOffice to your system `PATH`.
   - **macOS**:
     - Download from [LibreOffice’s website](https://www.libreoffice.org/download/download/) or
     - Use Homebrew:
       ```bash
       brew install --cask libreoffice
       ```

4. **Ollama & Vision Models**

   - [Install Ollama](https://github.com/jmorganca/ollama) for your OS.
   - Pull the required model:
     ```bash
     ollama pull llama3.2-vision
     ```
   - Test run to ensure your model is set up correctly.

5. **Poetry** (for local development only)
   - Recommended dependency manager if you’re cloning the repository to develop or modify **LlaMarker**.
   - **Linux/Mac**:
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     # (If not added to PATH automatically)
     export PATH="$HOME/.local/bin:$PATH"
     ```
   - **macOS (Homebrew)**:
     ```bash
     brew install poetry
     ```
   - **Windows**:  
     Follow instructions on [Poetry’s official site](https://python-poetry.org/docs/#installation).

---

## 🚀 Installation Options

### 1. Install via PyPI

The simplest approach—ideal if you just want to **use** LlaMarker rather than develop it:

```bash
pip install llamarker
```

- **Requires**: Python 3.10+
- After installing, you have access to two main commands:
  1. `llamarker` — CLI tool.
  2. `llamarker_gui` — Streamlit-based GUI for interactive use.

> **Note**: LibreOffice, Marker, and any optional OCR components need to be installed separately, if you plan to use their respective features.

---

### 2. Local Development Setup

If you plan to contribute or dive into the source code:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RevanKumarD/LlaMarker.git
   cd LlaMarker
   ```
2. **Install dependencies** using **Poetry**:
   ```bash
   poetry install
   ```
3. **Run LlaMarker locally**:
   - **CLI**:
     ```bash
     poetry run python llamarker/llamarker.py --directory <directory_path>
     ```
   - **GUI**:
     ```bash
     poetry run streamlit run llamarker/llamarker_gui.py
     ```

> No `requirements.txt` is provided; **Poetry** is the recommended (and supported) method for local development.

---

## 📌 Basic Usage

### CLI Usage

#### Installed via PyPI

- **Process a folder**:
  ```bash
  llamarker --directory <directory_path>
  ```
- **Process a single file**:
  ```bash
  llamarker --file <file_path>
  ```

#### Local Development

- **CLI**:
  ```bash
  poetry run python llamarker/llamarker.py --directory <directory_path>
  ```

---

### Streamlit GUI

A user-friendly interface to upload files/directories, parse them, and download results.

- **Installed via PyPI**:
  ```bash
  llamarker_gui
  ```
- **Local Development**:
  ```bash
  poetry run streamlit run llamarker/llamarker_gui.py
  ```

Open the link (e.g., `http://localhost:8501`) in your browser to start using **LlaMarker** via GUI.

---

## 🔧 Advanced Usage

### Command-Line Arguments

| Argument         | Description                                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--directory`    | **Root directory** containing documents to process.                                                                                                  |
| `--file`         | Path to a single file to process (optional).                                                                                                         |
| `--temp_dir`     | Temporary directory for intermediate files (optional).                                                                                               |
| `--save_pdfs`    | Flag to **save PDFs** in a separate directory (`PDFs`) under the root directory.                                                                     |
| `--output`       | Directory to **save output** files (optional). By default, parsed Markdown files are stored in `ParsedFiles` and images go under `ParsedFiles/pics`. |
| `--marker_path`  | Path to the **Marker** executable (optional). Auto-detects if `Marker` is in your `PATH`.                                                            |
| `--force_ocr`    | Force **OCR** on all pages, even if text is extractable. Useful for poorly formatted PDFs or PPTs.                                                   |
| `--languages`    | Comma-separated list of languages for OCR (default: `"en"`).                                                                                         |
| `--qa_evaluator` | Enable **QA Evaluator** for selecting the best response during image processing.                                                                     |
| `--verbose`      | Set verbosity level: **0** = WARNING, **1** = INFO, **2** = DEBUG (default: **0**).                                                                  |
| `--model`        | **Ollama** model for image analysis (default: `llama3.2-vision`). A local vision model is required for this to work.                                 |

---

### Example Commands

1. **Directory processing**:
   ```bash
   llamarker --directory /path/to/documents
   ```
2. **Single file with verbose output**:
   ```bash
   llamarker --file /path/to/document.docx --verbose 2
   ```
3. **Parsing with OCR in multiple languages**:
   ```bash
   llamarker --directory /path/to/docs --force_ocr --languages "en,de,fr"
   ```
4. **Save parsed PDFs to a custom folder**:
   ```bash
   llamarker --directory /path/to/docs --save_pdfs --output /path/to/output
   ```

---

## Output Structure

After processing, **LlaMarker** organizes files as follows:

- **`ParsedFiles`**
  - Contains the generated Markdown files.
  - **`pics`** — subfolder for extracted images.
- **`PDFs`**
  - Stores converted PDF files (if `--save_pdfs` is used).
- **`OutDir`**
  - Contains processed PDF files (used by the GUI).
- **`logs`**
  - Holds log files for each run (processing status, errors, etc.).

---

## Code Example

For local development, you can programmatically use **LlaMarker**:

```python
from llamarker import LlaMarker

llamarker = LlaMarker(
    input_dir="/path/to/documents",
    save_pdfs=True,
    output_dir="/path/to/output",
    verbose=1
)

# Process all documents in the specified directory
llamarker.process_documents()

# Generate summary info
results = llamarker.generate_summary()
for file, page_count in results:
    print(f"{file}: {page_count} pages")

# Generate analysis plots
llamarker.plot_analysis(llamarker.parent_dir)
```

---

## 🚧 Shortcomings & Future Updates

### Current Shortcomings:

1. **Limited OCR Accuracy for Complex Documents**  
   - While OCR works well for most cases, it may struggle with highly complex layouts or poorly scanned documents.
2. **No Direct Cloud Integration**  
   - Currently, LlaMarker only supports local processing. There’s no option to process files directly from cloud storage services like Google Drive or Dropbox.
3. **Basic Support for PPT and XLSX Parsing**  
   - Parsing of **PPT** and **XLSX** files is available but lacks advanced formatting support (e.g., slide layouts, complex charts).
4. **Poor XLSX to PDF Conversion**  
   - The current conversion of **XLSX** files to **PDF** results in poorly formatted output. Improvements are needed to handle large spreadsheets and complex tables.
5. **Manual Setup for Marker and LibreOffice**  
   - Users must manually install **Marker** and **LibreOffice**, which can be cumbersome for those unfamiliar with the setup process.

---

### Planned Future Updates:

1. **Enhanced OCR Capabilities**  
   - Improve OCR performance by integrating additional vision models for better handling of complex document layouts and multi-column formats.
2. **Cloud Storage Integration**  
   - Add support for uploading documents directly from cloud services (Google Drive, Dropbox, OneDrive).
3. **Improved PPT & XLSX Handling**  
   - Enhance parsing accuracy for **PPT** and **XLSX** files by adding better support for slides, tables, and embedded charts.
4. **Better XLSX to PDF Conversion**  
   - Improve the **XLSX to PDF** conversion process to handle large sheets, complex tables, and maintain proper formatting.
5. **Cross-Platform Installation Script**  
   - Provide an easy-to-use installation script for all platforms (Linux, Windows, macOS) to automate the setup of dependencies like **Marker** and **LibreOffice**.

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. Let’s make **LlaMarker** even more powerful—together. 🤝

---

## License

This project references the [Marker](https://github.com/VikParuchuri/marker) repository, which comes with its own license. Please review the Marker repo for licensing restrictions and guidelines.

© 2025 Revan Kumar Dhanasekaran. Released under the GPLv3 License.

---

## Acknowledgments

- **Huge thanks** to the [Marker](https://github.com/VikParuchuri/marker) project for providing an excellent foundation for parsing.
- **Special thanks** to the open-source community for continuous support and contributions.

---

<p align="center">
  <b>Happy Parsing!</b> 🌟
</p>
