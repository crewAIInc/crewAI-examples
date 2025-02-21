from langchain_community.document_loaders import PyPDFLoader
import sys
import os


class PdfReader:
    """
    Handles PDF file validation and text extraction using LangChain's PyPDFLoader.
    Provides error handling and validation for PDF processing operations.

    Attributes:
        pdf_path (str): Path to the PDF file to be processed
    """

    def __init__(self, pdf_path: str):
        """
        Initializes the PDF reader with a file path and validates the file.

        Args:
            pdf_path (str): Path to the PDF file

        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file is not a PDF
        """
        self.pdf_path = pdf_path
        self.validate_file()

    def validate_file(self):
        """
        Validates the PDF file existence and format.

        Performs two checks:
        1. File existence at the specified path
        2. File extension is '.pdf' (case-insensitive)

        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file does not have a .pdf extension
        """
        # Check if file exists in the specified path
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"The file {self.pdf_path} was not found.")

        # Verify file has PDF extension
        if not self.pdf_path.lower().endswith('.pdf'):
            raise ValueError("The file must be a PDF.")

    def read(self) -> str:
        """
        Extracts and concatenates text content from all pages of the PDF.
        Uses LangChain's PyPDFLoader for PDF processing.

        Returns:
            str: Concatenated text content from all PDF pages, stripped of leading/trailing whitespace

        Raises:
            SystemExit: If any error occurs during PDF processing

        Note:
            - Adds newline characters between pages
            - Strips leading/trailing whitespace from final output
            - Exits program with error message if PDF processing fails
        """
        try:
            # Initialize PDF loader
            loader = PyPDFLoader(self.pdf_path)

            # Extract pages from PDF
            pages = loader.load()

            # Concatenate text from all pages
            text = ""
            for page in pages:
                text += page.page_content + "\n"

            # Clean and return the extracted text
            return text.strip()

        except Exception as e:
            # Log error and exit program if PDF processing fails
            print(f"Error reading PDF file: {str(e)}")
            sys.exit(1)
