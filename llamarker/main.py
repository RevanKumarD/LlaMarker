import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from datetime import datetime
from llamarker.file_to_pdf_converter import FileToPDFConverter
from llamarker.img_processor import ImageProcessor
import subprocess
import tempfile
import shutil


class LlaMarker:
    """
    A class to handle document parsing, conversion, and analysis operations.
    """

    def __init__(self, input_dir: str = None, file_path: str = None, temp_dir: str = None, save_pdfs: bool = False, output_dir: str = None, logger: logging.Logger = None, marker_path: str = None, verbose: int = 0):
        """
        Initialize LlaMarker with a root directory for processing.

        Args:
            input_dir (str): Path to the input directory with files.
            file_path (str): Path to a single file to process.
            logger (logging.Logger): Logger instance for logging progress.
        """
        self.input_dir = Path(input_dir) if input_dir else None
        self.file_path = Path(file_path) if file_path else None
        self.logger = logger or logging.getLogger(__name__)
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp())
        self.output_dir = Path(output_dir) if output_dir else None
        self.save_dir = None
        self.verbose = verbose
        self.save_pdfs = save_pdfs
        if not marker_path:
            self.marker_path = shutil.which("marker")
            if not self.marker_path:
                self.logger.error("The 'marker' executable was not found in the system's PATH.")
                raise FileNotFoundError("The 'marker' executable is required but not found in the PATH.")
        else:
            self.marker_path = marker_path
        
        if self.input_dir:
            if self.output_dir:
                self.parent_dir = self.output_dir
            else:
                self.parent_dir = self.input_dir
            if self.save_pdfs:
                self.save_dir = self.parent_dir/"PDFs"
            if temp_dir:
                self.out_dir = self.temp_dir/"ParsedFiles"
            else:
                self.out_dir = self.parent_dir/"ParsedFiles"
        elif self.file_path:
            if self.output_dir:
                self.parent_dir = self.output_dir.parent
            else:
                self.parent_dir = self.input_dir.parent
            if self.save_pdfs:
                self.save_dir = self.parent_dir/"PDFs"
            if temp_dir:
                self.out_dir = self.temp_dir/"ParsedFiles"
            else:
                self.out_dir = self.parent_dir/"ParsedFiles"

        # Temporary folder to store converted PDFs
        self.logger.info(f"Temporary directory created at: {self.temp_dir}")

        # Validate input
        if self.file_path and not self.file_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.file_path}")

        # Validate input directory only if it is provided
        if self.input_dir and not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        self.setup_logging()
        self.file_converter = FileToPDFConverter(input_dir=self.input_dir, file_path=self.file_path, temp_dir=self.temp_dir, save_dir=self.save_dir, logger=self.logger)

    def setup_logging(self):
        """Configure logging for the LlaMarker operations based on verbosity level."""
        
        # Map verbosity levels to logging levels
        level_map = {
            0: logging.WARNING,  # Default level if verbose is not set (only warnings and errors)
            1: logging.INFO,     # Verbose level 1 (info, warnings, and errors)
            2: logging.DEBUG     # Verbose level 2 (debug, info, warnings, and errors)
        }
        
        log_level = level_map.get(self.verbose, logging.DEBUG)  # Default to DEBUG if invalid verbose level
        
        # Create log directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"llamarker_{timestamp}.log"

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging setup completed with level: %s", logging.getLevelName(log_level))

    def process_documents(self) -> None:
        """Process all documents in the root directory."""
        try:
            self.file_converter.convert_and_count_pages()
        except Exception as e:
            self.logger.error(f"Error during document processing: {e}")
            raise

    def parse_with_marker(self, workers: int = 4, force_ocr: bool = False, languages: str = "en") -> None:
        """
        Parse the OutDir folder using Marker and store the results in ParsedFiles.

        Args:
            workers (int): Number of worker threads to use (default: 4).
            force_ocr (bool): Whether to force OCR processing on all pages (default: False).
            languages (str): Comma-separated list of languages for OCR processing (default: "en").
        """
        self.logger.info(f"Starting parsing with Marker for directory: {self.temp_dir}")

        # Clean or create ParsedFiles directory
        if self.out_dir.exists():
            self.logger.info(f"Cleaning existing ParsedFiles directory: {self.out_dir}")
            for item in self.out_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        self.out_dir.mkdir(exist_ok=True)

        if self.temp_dir.is_dir():
            # Run Marker command for the current directory
            try:
                command = [
                    self.marker_path,
                    str(self.temp_dir),
                    "--output_dir",
                    str(self.out_dir),
                    "--workers",
                    str(workers),
                ]
                
                # Add force OCR option if enabled
                if force_ocr:
                    command.append("--force_ocr")
                
                # Add languages option
                command.extend(["--languages", languages])

                self.logger.info(f"Running Marker command: {' '.join(command)}")
                subprocess.run(command, check=True)
                self.logger.info(f"Parsing completed for directory: {self.temp_dir}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Marker command failed for {self.temp_dir}: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Error during parsing for {self.temp_dir}: {e}")
                raise

        self.logger.info(f"Parsing completed successfully for all file. Parsed files saved in {self.out_dir}")


    def process_subdirectories(self, model: str = 'llama3.2-vision', qa_evaluator: bool = True) -> None:
        """
        Process all directories (including nested subdirectories) in the root directory with ImageProcessor.

        Args:
            model (str): Name of the Ollama model to use.
        """
        self.logger.info(f"Processing directories in: {self.out_dir}")

        # Recursively traverse all directories
        for subdir in self.out_dir.rglob("*"):
            if subdir.is_dir():
                self.logger.info(f"Processing directory: {subdir}")
                try:
                    # Check if the directory contains an .md file
                    markdown_files = list(subdir.glob("*.md"))
                    if not markdown_files:
                        self.logger.warning(f"Skipping directory {subdir}: No Markdown (.md) file found.")
                        continue

                    # Process the directory using ImageProcessor
                    processor = ImageProcessor(folder_path=str(subdir), model=model, logger=self.logger, qa_evaluator=qa_evaluator)
                    processor.process_images()
                    processor.update_markdown()
                    processor.summarize_results()
                except Exception as e:
                    self.logger.error(f"Failed to process directory {subdir}: {e}")

        if self.temp_dir.exists():
            self.file_converter.cleanup()

        self.logger.info("Finished processing all files.")

    
    def generate_summary(self) -> List[Tuple[str, int]]:
        """
        Generate a summary of processed documents.

        Returns:
            List[Tuple[str, int]]: List of (filename, page_count) tuples
        """
        return self.file_converter.get_results()

    def plot_analysis(self, output_dir: Optional[str] = None) -> None:
        """
        Generate and save analysis plots.

        Args:
            output_dir (Optional[str]): Directory to save plots. If None, uses current directory.
        """
        try:
            if output_dir:
                plot_dir = Path(output_dir)
                plot_dir.mkdir(exist_ok=True)

            self.file_converter.plot_page_counts()

            if output_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plt.savefig(plot_dir / f"page_counts.png")
                self.logger.info(f"Plot saved to {plot_dir}")

            self.logger.info("Analysis plots generated successfully.")
        except Exception as e:
            self.logger.error(f"Error generating analysis plots: {e}")
            raise


def main():
    """Main entry point for the LlaMarker application."""
    parser = argparse.ArgumentParser(
        description="Process and analyze documents with LlaMarker."
    )
    parser.add_argument(
        "--directory", type=str, help="Root directory containing documents to process", default=None
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Single file to process (optional)",
        default=None,
    )
    parser.add_argument(
        "--temp_dir",
        type=str,
        help="Temporary directory for intermediate files (optional)",
        default=None,
    )
    parser.add_argument(
        "--save_pdfs",
        action="store_true",
        help="Flag to save PDFs in a separate directory.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Directory to save output files (optional)",
        default=None,
    )
    parser.add_argument(
        "--marker_path",
        type=str,
        help="path of the marker executable (optional)",
        default=None,
    )

    # Argument for force OCR
    parser.add_argument(
        "--force_ocr",
        action="store_true",  # Boolean flag; if present, it's True
        help="Force OCR processing on the entire document, even for pages that might contain extractable text.",
    )

    # Argument for specifying languages
    parser.add_argument(
        "--languages",
        type=str,
        help='Comma-separated list of languages for OCR processing (e.g., "en,fr,de"). Default is "en".',
        default="en",
    )

    # Argument for enabling or disabling QA Evaluator
    parser.add_argument(
        "--qa_evaluator",
        action="store_true",  # Boolean flag; if present, it's True
        help="Enable or disable the QA Evaluator for selecting the best response during image processing.",
    )

    # New argument for verbose
    parser.add_argument(
        "--verbose",
        type=int,
        choices=[0, 1, 2],
        help="set verbosity level: 0 for WARNING, 1 for INFO, 2 for DEBUG (default: 0)",
        default=0,
    )
    parser.add_argument("--model", type=str, default='llama3.2-vision', help="Ollama model to query.")

    args = parser.parse_args()

    try:
        llamarker = LlaMarker(
            input_dir=args.directory,
            file_path=args.file,
            temp_dir=args.temp_dir,
            save_pdfs=args.save_pdfs,
            output_dir=args.output,
            marker_path=args.marker_path,
            verbose=args.verbose
        )

        # Step 1: Process documents (convert and count pages)
        llamarker.process_documents()

        # Step 2: Parse documents with Marker
        llamarker.parse_with_marker(force_ocr=args.force_ocr, languages=args.languages)

        # Step 3: Enriched Parsed files
        llamarker.process_subdirectories(model=args.model, qa_evaluator=args.qa_evaluator)

        # Step 4: Print summary
        print("\nDocument Processing Summary:")
        print("-" * 30)
        for file_name, page_count in llamarker.generate_summary():
            print(f"{file_name}: {page_count} pages")

        # Step 5: Generate analysis plots
        llamarker.plot_analysis(llamarker.parent_dir)

        print("\nProcessing completed successfully!")

    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Fatal error during execution: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
