import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from datetime import datetime
from file_to_pdf_converter import FileToPDFConverter
from img_processor import ImageProcessor
import subprocess
import tempfile
import shutil


class RevParser:
    """
    A class to handle document parsing, conversion, and analysis operations.
    """

    def __init__(self, input_dir: str = None, file_path: str = None, temp_dir: str = None, save_pdfs = False, output_dir: str = None, logger: logging.Logger = None, marker_path: str = None):
        """
        Initialize RevParser with a root directory for processing.

        Args:
            input_dir (str): Path to the input directory with files.
            file_path (str): Path to a single file to process.
            logger (logging.Logger): Logger instance for logging progress.
        """
        self.input_dir = Path(input_dir) if input_dir else None
        self.file_path = Path(file_path) if file_path else None
        self.logger = logger or logging.getLogger(__name__)
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp())
        self.output_dir = output_dir
        if not marker_path:
            self.marker_path = shutil.which("marker")
            if not self.marker_path:
                self.logger.error("The 'marker' executable was not found in the system's PATH.")
                raise FileNotFoundError("The 'marker' executable is required but not found in the PATH.")
        else:
            self.marker_path = marker_path
        
        if self.input_dir:
            if self.output_dir:
                self.parent_dir = self.output_dir.parent
            else:
                self.parent_dir = self.input_dir.parent
            if save_pdfs:
                self.save_dir = self.parent_dir/"PDFs"
            self.out_dir = self.parent_dir/"ParsedFiles"
        elif self.file_path:
            if self.output_dir:
                self.parent_dir = self.output_dir.parent
            else:
                self.parent_dir = self.input_dir.parent
            if save_pdfs:
                self.save_dir = self.parent_dir/"PDFs"
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
        """Configure logging for the RevParser operations."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"rev_parser_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def process_documents(self) -> None:
        """Process all documents in the root directory."""
        try:
            self.file_converter.convert_and_count_pages()
        except Exception as e:
            self.logger.error(f"Error during document processing: {e}")
            raise

    def parse_with_marker(self, workers: int = 4) -> None:
        """
        Parse the OutDir folder using Marker and store the results in ParsedFiles.

        Args:
            workers (int): Number of worker threads to use (default: 4).
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

    def process_subdirectories(self, model: str = 'llama3.2-vision') -> None:
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
                    processor = ImageProcessor(folder_path=str(subdir), model=model, logger=self.logger)
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
                plt.savefig(plot_dir / f"page_counts_{timestamp}.png")
                self.logger.info(f"Plot saved to {plot_dir}")

            self.logger.info("Analysis plots generated successfully.")
        except Exception as e:
            self.logger.error(f"Error generating analysis plots: {e}")
            raise


def main():
    """Main entry point for the RevParser application."""
    parser = argparse.ArgumentParser(
        description="Process and analyze documents with RevParser."
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
    parser.add_argument("--model", type=str, default='llama3.2-vision', help="Ollama model to query.")

    args = parser.parse_args()

    try:
        rev_parser = RevParser(
            input_dir=args.directory,
            file_path=args.file,
            temp_dir=args.temp_dir,
            save_pdfs=args.save_pdfs,
            output_dir=args.output,
            marker_path=args.marker_path
        )

        # Step 1: Process documents (convert and count pages)
        rev_parser.process_documents()

        # Step 2: Parse documents with Marker
        rev_parser.parse_with_marker()

        # Step 3: Enriched Parsed files
        rev_parser.process_subdirectories(model=args.model)

        # Step 4: Print summary
        print("\nDocument Processing Summary:")
        print("-" * 30)
        for file_name, page_count in rev_parser.generate_summary():
            print(f"{file_name}: {page_count} pages")

        # Step 5: Generate analysis plots
        rev_parser.plot_analysis(rev_parser.parent_dir)

        print("\nProcessing completed successfully!")

    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Fatal error during execution: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
