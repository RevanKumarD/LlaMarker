# <p align="center"><img src="llamarker/assets/Llamarker_logo.png" alt="LlaMarker Logo" width="200"></p>

<h1 align="center">🖍️ LlaMarker</h1>

<p align="center">
  <b>Your go-to tool for converting and parsing documents into clean, well-structured Markdown!</b><br>
  <i>Fast, intuitive, and entirely local 💻🚀.</i>
</p>

<div align="center">
  
[![Python Versions](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License](https://img.shields.io/badge/License-Refer%20Marker%20Repo-lightgrey.svg)](https://github.com/VikParuchuri/marker)

</div>

---

## ✨ Key Features

- **All-in-One Parsing**: Supports **TXT**, **DOCX**, **PDF**, **PPT**, **XLSX**, and more—even processes images inside documents.
- **Visual Content Extraction**: Utilizes **Llama 3.2 Vision** to detect images, tables, charts, and diagrams, converting them into rich Markdown.
- **Built with Marker**: Extends the open-source [Marker](https://github.com/VikParuchuri/marker) parser to handle complex content types **locally**.
- **Local-First Privacy**: No cloud, no external servers—**all processing** happens on your machine.

---

## 🚀 How It Works

1. **Parsing & Conversion**  
   - Parses and converts multiple file types (`.txt`, `.docx`, `.pdf`, `.ppt`, `.xlsx`, etc.) into Markdown.  
   - Leverages **Marker** for accurate and efficient parsing of both text and visual elements.  
   - Extracts images, charts, and tables, embedding them in Markdown.  
   - (Optional) Converts documents into PDFs using **LibreOffice** for easy viewing.

2. **Visual Analysis**  
   - Distinguishes logos from content-rich images.  
   - Extracts and preserves the original language from images.

3. **Fast & Efficient**  
   - Supports parallel processing for faster handling of large folders.

4. **Streamlit GUI**  
   - A user-friendly interface to upload and parse files or entire directories.  
   - Download results directly from the GUI.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
   - [Requirements](#requirements)
   - [OS-Specific Setup](#os-specific-setup)
   - [Installing LlaMarker](#installing-llamarker)
3. [Usage](#usage)
   - [CLI Usage](#cli-usage)
   - [Example Commands](#example-commands)
   - [Streamlit GUI](#running-the-streamlit-gui)
4. [Output Structure](#output-structure)
5. [Code Example](#code-example)
6. [Contributing](#contributing)
7. [License](#license)
8. [Acknowledgments](#acknowledgments)

---

## Features

- **Document Conversion**  
  Converts `.txt`, `.docx`, and other supported file types into `.pdf` using **LibreOffice**.

- **Page Counting**  
  Automatically counts pages in PDFs using **PyPDF2**.

- **Image Processing**  
  Analyzes images to differentiate logos from content-rich images. Extracts relevant data and updates the corresponding Markdown file.

- **Markdown Parsing**  
  Uses **Marker** to generate clean, structured Markdown files from parsed PDFs.

- **Multilingual Support**  
  Maintains the original language of the content during extraction.

- **Data Visualization**  
  Generates analysis plots based on the page counts of processed documents.

---

## Installation

### Requirements
1. **Python 3.10+**  
2. **[Marker](https://github.com/VikParuchuri/marker)** installed locally or available in your `PATH`.
3. **LibreOffice** (for document conversion; optional if you only want to parse existing PDFs).

### OS-Specific Setup

#### Linux (Ubuntu/Debian example)
```bash
sudo apt update
sudo apt install libreoffice
```
Make sure `Marker` is installed and available in your PATH, or specify its path with `--marker_path`.

#### Windows
1. **[Download and Install LibreOffice](https://www.libreoffice.org/download/download/)**
   - During installation, ensure you add LibreOffice to the system path (optional, but recommended).
2. **Marker Installation**
   - Download the latest release/binary from the [Marker GitHub repo](https://github.com/VikParuchuri/marker).
   - Place it in a directory and add that directory to your system `PATH`.
   - Alternatively, use the `--marker_path` argument to specify its location.

#### macOS
1. **[Install LibreOffice](https://www.libreoffice.org/download/download/)** (Drag-and-drop to `Applications` folder).
2. **Homebrew users**:
   ```bash
   brew install --cask libreoffice
   ```
3. **Marker Installation**
   - Download the latest macOS binary from the [Marker GitHub repo](https://github.com/VikParuchuri/marker).
   - Ensure the binary is placed in a directory in your `PATH`.

### Installing LlaMarker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RevanKumarD/LlaMarker.git
   cd LlaMarker
   ```

2. **Install Dependencies** (using [Poetry](https://python-poetry.org/)):
   ```bash
   poetry install
   ```
   > Note: A `post_install` script for installing LibreOffice is included for Linux machines only. On Windows or macOS, you must install LibreOffice manually.

---

## 🔍 Usage

### CLI Usage

```bash
poetry run python llamarker.py --directory <directory_path> [options]
```

**Arguments**:

| Argument         | Description                                                                                                                                                                                        |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--directory`    | **Root directory** containing documents to process.                                                                                                                                               |
| `--file`         | Path to a single file to process (optional).                                                                                                                                                      |
| `--temp_dir`     | Temporary directory for intermediate files (optional).                                                                                                                                            |
| `--save_pdfs`    | Flag to **save PDFs** in a separate directory (`PDFs`) under the root directory.                                                                                                                   |
| `--output`       | Directory to **save output** files (optional). By default, parsed Markdown files are stored in the `ParsedFiles` folder under the root directory, and images go under `pics` in `ParsedFiles`.    |
| `--marker_path`  | Path to the **Marker** executable (optional). Program should auto-recognize the `Marker` path if it’s in your `PATH`.                                                                              |
| `--force_ocr`    | Force **OCR** on all pages, even if text is extractable. Helpful for poorly formatted PDFs or PPTs.                                                                                                |
| `--languages`    | Comma-separated list of languages for OCR (default: `"en"`).                                                                                                                                       |
| `--qa_evaluator` | Enable **QA Evaluator** for selecting the best response during image processing.                                                                                                                   |
| `--verbose`      | Set verbosity level: **0** = WARNING, **1** = INFO, **2** = DEBUG (default: **0**).                                                                                                                |
| `--model`        | **Ollama** model for image analysis (default: `llama3.2-vision`). A local vision model is required for this to work.                                                                               |

---

### Example Commands

1. **Processing a directory**  
   ```bash
   poetry run python llamarker.py --directory /path/to/documents
   ```

2. **Processing a single file with verbose output**  
   ```bash
   poetry run python llamarker.py --file /path/to/document.docx --verbose 2
   ```

3. **Parsing with OCR in multiple languages**  
   ```bash
   poetry run python llamarker.py --directory /path/to/documents --force_ocr --languages "en,de,fr"
   ```

4. **Saving parsed PDFs separately**  
   ```bash
   poetry run python llamarker.py --directory /path/to/documents --save_pdfs --output /path/to/output
   ```

---

### Running the Streamlit GUI

LlaMarker also comes with a **Streamlit**-based graphical user interface, making it simpler to:
- Upload files or entire directories
- Parse documents
- Download the resulting Markdown files

To launch the Streamlit app:

```bash
poetry run streamlit run llamarker_gui.py
```

Once running, open the provided local URL in your browser to interact with LlaMarker.

---

## Output Structure

- **`OutDir`**  
  Contains processed PDF files (used by the GUI).

- **`ParsedFiles`**  
  Contains the generated **Markdown** files.  
  - **`pics`** subfolder: Holds extracted images from the processed files.

- **`PDFs`**  
  Stores converted PDF files (if `--save_pdfs` is used).

- **`logs`**  
  Stores log files for each run, helping you track processing status and errors.

---

## Code Example

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

# Generate summary information
results = llamarker.generate_summary()
for file, pages in results:
    print(f"{file}: {pages} pages")

# Generate analysis plots
llamarker.plot_analysis(llamarker.parent_dir)
```

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. We appreciate all the help we can get in making **LlaMarker** even better.

---

## License

This project references the [Marker](https://github.com/VikParuchuri/marker) repository, which comes with its own license. Please review the Marker repo for licensing restrictions and guidelines.

---

## Acknowledgments

- **Huge thanks** to the [Marker](https://github.com/VikParuchuri/marker) project for providing an excellent foundation for parsing PDFs.
- **Special thanks** to the open-source community for continuous support and contributions.

---

<p align="center">
  <b>Happy Parsing!</b> 🌟
</p>