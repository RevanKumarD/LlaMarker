# ![LlaMarker Logo](llamarker/assets/Llamarker_logo.png)

# Llamarker

**LlaMarker** is a comprehensive Python package designed for universal parsing and document conversion. It provides end-to-end capabilities for converting files into PDFs, extracting text and structured content (including images, tables, graphs, and flowcharts), and converting these into clean Markdown files. Its primary focus is on maintaining accuracy and supporting multilingual content.

---

## Features

- **Document Conversion**: Converts `.txt`, `.docx`, and other supported file types into PDF using LibreOffice.
- **Page Counting**: Automatically counts pages in PDFs using PyPDF2.
- **Image Processing**: Analyzes images to distinguish logos from content-rich images, extracts relevant information, and updates the corresponding Markdown file.
- **Markdown Parsing**: Uses Marker to generate clean, structured Markdown files from parsed PDFs.
- **Multilingual Support**: Maintains the original language of the content during extraction.
- **Data Visualization**: Generates analysis plots based on document page counts.

---

## How It Works

### 1. Document Processing
- Converts text-based files into PDFs.
- Copies existing PDFs to the output directory while maintaining the folder structure.
- Counts pages in all processed PDFs.

### 2. Parsing with Marker
- Uses Marker to extract content from PDFs and generate Markdown files.
- Supports parallel processing with multiple workers for efficient parsing.

### 3. Image Analysis
- Identifies logos and content images using the Ollama vision model.
- Extracts information from content-rich images and updates the corresponding Markdown file.
- Translates extracted information to the original language, ensuring content integrity.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RevanKumarD/LlaMarker.git
   cd LlaMarker
   ```

2. Install dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure LibreOffice is installed for document conversion:
   ```bash
   sudo apt install libreoffice
   ```

---

## Usage

```bash
python RevParser.py <directory_path> --model llama3.2-vision
```

### Arguments:
- `<directory_path>`: Root directory containing documents to process.
- `--model`: Ollama model for image processing (default: `llama3.2-vision`).

---

## Example

1. **Converting Documents**:
   ```bash
   python RevParser.py /path/to/documents
   ```

2. **Viewing Results**:
   Processed PDFs and Markdown files will be available in the `OutDir` and `ParsedFiles` directories, respectively.

---

## Output Structure

- **OutDir**: Contains processed PDF files.
- **ParsedFiles**: Contains Markdown files generated from parsed PDFs.
- **logs**: Stores log files for each run, helping track processing status and errors.

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

Special thanks to the contributors and the open-source community for their invaluable support.

---

Let me know if you want further adjustments, including the specific path for the logo!