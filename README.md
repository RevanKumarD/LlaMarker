# RevParser: Universal File Parser Locally

RevParser is a Python package that efficiently parses the structured information from any complex docs of any type. It uses **LibreOffice** for accurate PDF conversion, ensuring layout preservation. Temporary file handling ensures a clean workflow.

---

## Features
- **File Conversion**: Convert `.txt` and `.docx` files to PDFs.
- **Image Processing**: Analyze images and extract structured content.
- **Temporary File Management**: Store files temporarily unless explicitly saved.
- **Cross-Platform**: Works on both Linux and Windows.

---

## Pre-requisites

Before using this package, ensure **LibreOffice** is installed:

- **Linux**:
  Install LibreOffice via terminal:
  ```bash
  sudo apt update
  sudo apt install libreoffice
  ```

- **Windows**:
  Download and install LibreOffice from the official website:
  [LibreOffice Download](https://www.libreoffice.org/download/)

To verify installation:
```bash
libreoffice --version   # For Linux
soffice --version       # For Windows
```

---

## Installation

Install RevParser using `pip`:

```bash
pip install revparser
```

---

## Usage

### 1. File Conversion

Convert `.txt` and `.docx` files in a directory to PDFs:

```python
from revparser.file_to_pdf_converter import FileToPDFConverter

# Initialize the converter
converter = FileToPDFConverter(input_dir="path/to/input", save_dir="path/to/save")

# Convert files and get results
try:
    converter.convert_and_count_pages()
    for pdf, pages in converter.get_results():
        print(f"{pdf} - {pages} pages")
finally:
    converter.cleanup()
```

- **`input_dir`**: Directory containing files to process.
- **`save_dir`** (optional): Directory to save PDFs permanently.

---

### 2. Image Processing

Analyze images and extract content:

```python
from revparser.img_processor import ImageProcessor

# Initialize the image processor
processor = ImageProcessor(folder_path="path/to/images")
processor.process_images()
```

---

## Requirements

- Python 3.8 or later
- PyPDF2
- LibreOffice (pre-installed)

Install required dependencies:

```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome! Follow these steps:
1. Fork the repository.
2. Create a new branch for your feature.
3. Submit a pull request.

---

## License

This project is licensed under the MIT License.
