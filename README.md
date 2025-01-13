<p align="center" style="margin: 0; padding: 0;">
  <img src="llamarker/assets/Llamarker_logo.png" alt="LlaMarker Logo" width="200">
</p>

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

- ✨ **All-in-One Parsing**: Supports **TXT**, **DOCX**, **PDF**, **PPT**, **XLSX**, and more—even processes images inside documents.
- 🖼️ **Visual Content Extraction**: Utilizes **Llama 3.2 Vision** to detect images, tables, charts, and diagrams, converting them into rich Markdown.
- 🏗️ **Built with Marker**: Extends the open-source [Marker](https://github.com/VikParuchuri/marker) parser to handle complex content types **locally**.
- 🛡️ **Local-First Privacy**: No cloud, no external servers—**all processing** happens on your machine.

---

## 🚀 How It Works

1. **Parsing & Conversion**

   - Parses and converts multiple file types (`.txt`, `.docx`, `.pdf`, `.ppt`, `.xlsx`, etc.) into Markdown.
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
2. [Installation](#installation)
   - [Requirements](#requirements)
   - [Pre-Requisites](#pre-requisites)
     - [Linux (Ubuntu/Debian)](#linux-ubuntudebian-example)
     - [Windows](#windows)
     - [macOS](#macos)
   - [Poetry Installation](#poetry-installation)
   - [Installing Ollama & Vision Models](#installing-ollama--vision-models)
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

## ✨ Features

- 📄 **Document Conversion**  
  Converts `.txt`, `.docx`, and other supported file types into `.pdf` using **LibreOffice**.

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

## 🛠️ Installation

### 🔧 Requirements

1. **Python 3.10+** – Core language for running **LlaMarker**.
2. **[Marker](https://github.com/VikParuchuri/marker)** – Open-source parser tool. Ensure it's installed locally or available in your `PATH`.
3. **LibreOffice** – Required for document conversion (_Optional if you only need to parse PDFs_).
4. _(Recommended)_ **Poetry** – Dependency manager for Python.

---

### ⚙️ Pre-Requisites

Below are the essential steps to get your environment ready for **LlaMarker**. Follow the instructions based on your OS.

---

### 🖥️ **LibreOffice Installation**

1. **Linux**

   - Update your package list and install LibreOffice:
     ```bash
     sudo apt update
     sudo apt install libreoffice
     ```
   - Ensure **Marker** is installed and available in your `PATH`. You can also specify its location using the `--marker_path` argument.

2. **Windows**

   - [Download and Install LibreOffice](https://www.libreoffice.org/download/download/).
   - During installation, enable the option to add LibreOffice to your system `PATH` (optional but recommended).

3. **macOS**
   - **Option 1**: Download LibreOffice from [LibreOffice’s website](https://www.libreoffice.org/download/download/) and drag it into the `Applications` folder.
   - **Option 2 (Homebrew)**:
     ```bash
     brew install --cask libreoffice
     ```

---

### 🛠️ **Poetry Installation**

1. **Linux / macOS**

   - Install Poetry using the official installation script:
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - _(If Poetry is not added to your `PATH` automatically)_ Add it manually:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```
     _(You can add this line to your shell configuration file, e.g., `.bashrc` or `.zshrc`, for permanent access.)_

2. **macOS (Homebrew)**

   - Alternatively, you can use Homebrew:
     ```bash
     brew install poetry
     ```

3. **Windows**

   - Download the installer from [Poetry’s official site](https://python-poetry.org/docs/#installation) and run it.
   - After installation, open a new terminal and verify Poetry is installed:
     ```bash
     poetry --version
     ```

4. **Windows Subsystem for Linux (WSL)**
   - Follow the **Linux** installation steps.

---

### 🧠 **Installing Ollama & Vision Models**

1. **Install Ollama**  
   Follow the instructions provided on the [Ollama GitHub repo](https://github.com/jmorganca/ollama) for your OS.

2. **Download Vision Models**  
   Once Ollama is installed, pull the required model:

   ```bash
   ollama pull llama3.2-vision
   ```

3. **Verify Model Setup**  
   Run a sample inference to ensure everything is working correctly.

---

### 🚀 **Installing LlaMarker**

1. Clone the repository:

   ```bash
   git clone https://github.com/RevanKumarD/LlaMarker.git
   cd LlaMarker
   ```

2. Install dependencies using **Poetry**:

   ```bash
   poetry install
   ```

   > **Note**: A `post_install` script for installing LibreOffice is included for Linux systems only. On Windows or macOS, install LibreOffice manually as described above.

---

### 💡 Quick Tips

- Make sure **Python 3.10+** is installed before proceeding.
- If you encounter issues during the installation, refer to the [official Poetry documentation](https://python-poetry.org/docs/#installation).
- Ensure that **Marker** and **LibreOffice** are correctly added to your `PATH` for seamless execution of **LlaMarker**.

---

## 🔍 Usage

### CLI Usage

```bash
poetry run python llamarker/llamarker.py --directory <directory_path> [options]
```

**Arguments**:

| Argument         | Description                                                                                                                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--directory`    | **Root directory** containing documents to process.                                                                                                                                            |
| `--file`         | Path to a single file to process (optional).                                                                                                                                                   |
| `--temp_dir`     | Temporary directory for intermediate files (optional).                                                                                                                                         |
| `--save_pdfs`    | Flag to **save PDFs** in a separate directory (`PDFs`) under the root directory.                                                                                                               |
| `--output`       | Directory to **save output** files (optional). By default, parsed Markdown files are stored in the `ParsedFiles` folder under the root directory, and images go under `pics` in `ParsedFiles`. |
| `--marker_path`  | Path to the **Marker** executable (optional). Program should auto-recognize the `Marker` path if it’s in your `PATH`.                                                                          |
| `--force_ocr`    | Force **OCR** on all pages, even if text is extractable. Helpful for poorly formatted PDFs or PPTs.                                                                                            |
| `--languages`    | Comma-separated list of languages for OCR (default: `"en"`).                                                                                                                                   |
| `--qa_evaluator` | Enable **QA Evaluator** for selecting the best response during image processing.                                                                                                               |
| `--verbose`      | Set verbosity level: **0** = WARNING, **1** = INFO, **2** = DEBUG (default: **0**).                                                                                                            |
| `--model`        | **Ollama** model for image analysis (default: `llama3.2-vision`). A local vision model is required for this to work.                                                                           |

---

### Example Commands

{ Again this for local developement. }

1. **Processing a directory**

   ```bash
   poetry run python llamarker/llamarker.py --directory /path/to/documents
   ```

2. **Processing a single file with verbose output**

   ```bash
   poetry run python llamarker/llamarker.py --file /path/to/document.docx --verbose 2
   ```

3. **Parsing with OCR in multiple languages**

   ```bash
   poetry run python llamarker/llamarker.py --directory /path/to/documents --force_ocr --languages "en,de,fr"
   ```

4. **Saving parsed PDFs separately**
   ```bash
   poetry run python llamarker/llamarker.py --directory /path/to/documents --save_pdfs --output /path/to/output
   ```

---

### Running the Streamlit GUI

{Comment: The below is for local development and testing. For general users all they need to do is just run llamarker_gui in the terminal.}

LlaMarker also comes with a **Streamlit**-based graphical user interface, making it simpler to:

- Upload files (including multiple files at once) or entire directories
- Parse documents
- Download the resulting Markdown files

To launch the Streamlit app:

```bash
poetry run streamlit run llamarker/llamarker_gui.py
```

Once running, open the provided local URL in your browser to interact with **LlaMarker**.

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

Here’s a quick example showing how to leverage the pdf conversion utilities:

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

Contributions are welcome! Feel free to open an issue or submit a pull request. We appreciate all the help we can get in making **LlaMarker** even better. 🤝

---

## License

This project references the [Marker](https://github.com/VikParuchuri/marker) repository, which comes with its own license. Please review the Marker repo for licensing restrictions and guidelines.

© 2025 Revan Kumar Dhanasekaran. Released under the GPLv3 License.

---

## Acknowledgments

- **Huge thanks** to the [Marker](https://github.com/VikParuchuri/marker) project for providing an excellent foundation for parsing PDFs.
- **Special thanks** to the open-source community for continuous support and contributions.

---

<p align="center">
  <b>Happy Parsing!</b> 🌟
</p>
