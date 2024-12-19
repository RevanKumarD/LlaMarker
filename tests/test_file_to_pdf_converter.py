import pytest
import logging
from pathlib import Path
from revparser.file_to_pdf_converter import FileToPDFConverter
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="session")
def logger():
    """Fixture to configure and return a logger for testing."""
    logger = logging.getLogger("RevParserTest")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


@pytest.fixture
def temp_input_dir(tmp_path):
    """Fixture to create a temporary input directory with test files."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create test files
    test_file_txt = input_dir / "test1.txt"
    test_file_txt.write_text("This is a test text file.")

    test_file_docx = input_dir / "test2.docx"
    test_file_docx.write_text("This is a mock DOCX file.")  # Placeholder for DOCX file

    return input_dir


@pytest.fixture
def temp_save_dir(tmp_path):
    """Fixture to create a temporary save directory."""
    save_dir = tmp_path / "output"
    save_dir.mkdir()
    return save_dir


@patch("shutil.which", return_value="/usr/bin/libreoffice")
@patch("subprocess.run")
def test_convert_and_count_pages(mock_subprocess, mock_libreoffice, temp_input_dir, temp_save_dir, logger):
    """Test file conversion and page counting."""
    converter = FileToPDFConverter(input_dir=temp_input_dir, temp_dir=temp_save_dir, logger=logger)

    # Mock the PDF counting to avoid actual file handling
    with patch("revparser.file_to_pdf_converter.PdfReader") as mock_pdf_reader:
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [1, 2]  # Simulate a 2-page PDF
        mock_pdf_reader.return_value = mock_reader_instance

        # Simulate file creation after subprocess.run
        def mock_run_side_effect(*args, **kwargs):
            output_dir = kwargs.get("cwd", temp_save_dir)
            logger.debug(f"mock_run_side_effect executed with cwd={output_dir}")
            for file in temp_input_dir.glob("*.txt"):
                pdf_path = temp_save_dir / f"{file.stem}.pdf"
                pdf_path.write_text("Mock PDF content")
                logger.debug(f"Created mock PDF {pdf_path}")
            for file in temp_input_dir.glob("*.docx"):
                pdf_path = temp_save_dir / f"{file.stem}.pdf"
                pdf_path.write_text("Mock PDF content")
                logger.debug(f"Created mock PDF {pdf_path}")

        mock_subprocess.side_effect = mock_run_side_effect

        # Run the conversion
        converter.convert_and_count_pages()

        # Assert subprocess.run was called for both files
        assert mock_subprocess.call_count == 2

        # Check files in save_dir
        results = converter.get_results()
        assert len(results) == 2  # Two files processed
        for pdf_file, pages in results:
            pdf_path = Path(pdf_file)
            logger.debug(f"Checking if {pdf_path} exists.")
            assert pdf_path.exists()  # Ensure the PDF file exists
            assert pdf_path.parent == temp_save_dir  # File was saved to save_dir
            assert pages == 2  # Mocked page count


@patch("shutil.which", return_value=None)  # Mock LibreOffice check
@patch("pathlib.Path.exists", return_value=True)  # Mock input directory existence
def test_validate_libreoffice(mock_path_exists, mock_shutil_which, logger):
    """Test that the program validates LibreOffice installation."""
    with pytest.raises(EnvironmentError, match="LibreOffice is not installed"):
        FileToPDFConverter(input_dir="/nonexistent/path", logger=logger)


def test_cleanup(temp_input_dir, temp_save_dir, logger):
    """Test that cleanup removes the temporary directory."""
    converter = FileToPDFConverter(input_dir=temp_input_dir, save_dir=temp_save_dir, logger=logger)
    temp_dir = converter.temp_dir

    # Ensure the temp directory exists before cleanup
    assert temp_dir.exists()

    # Call cleanup
    converter.cleanup()

    # Ensure the temp directory is removed
    assert not temp_dir.exists()
