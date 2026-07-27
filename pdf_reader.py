"""
pdf_reader.py

Reads PDF files and extracts text.
"""

import fitz
from pathlib import Path


class PDFReader:
    """
    Reads PDF files and extracts text page by page.
    """

    def __init__(self):
        pass

    def extract_text(self, pdf_path):
        """
        Extract text from a PDF.

        Parameters:
            pdf_path (str or Path)

        Returns:
            list[str]
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        extracted_lines = []

        try:
            document = fitz.open(pdf_path)

            for page_number, page in enumerate(document, start=1):

                text = page.get_text()

                for line in text.splitlines():

                    cleaned_line = line.strip()

                    if cleaned_line:
                        extracted_lines.append(cleaned_line)

            document.close()

            return extracted_lines

        except Exception as error:
            print(f"Error reading PDF: {error}")
            return []


if __name__ == "__main__":

    reader = PDFReader()

    sample_pdf = "uploads/old/sample.pdf"

    try:
        lines = reader.extract_text(sample_pdf)

        print("\nExtracted Text")
        print("-" * 40)

        for line in lines:
            print(line)

    except Exception as e:
        print(e)