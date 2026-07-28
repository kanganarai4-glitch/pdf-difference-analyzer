"""
pdf_reader.py  —  Milestone 5

Responsible for:
    Reading a PDF file and extracting all text from every page.

How it works
─────────────────────────────────────────────────────────────────
  Uses PyMuPDF (fitz) to open each page and call get_text().
  Returns a clean list of non-empty lines.

  Example:
      reader = PDFReader()
      lines  = reader.extract_text("uploads/old/Login.pdf")
      # → ["Login", "Username", "Password", "Forgot Password"]

Why line-by-line?
─────────────────────────────────────────────────────────────────
  The comparison engine (comparator.py) works by comparing
  individual lines of text. Breaking the PDF into lines here
  makes that step simpler.
"""

import fitz  # PyMuPDF — pip install pymupdf
from pathlib import Path


# ── PDFReader ─────────────────────────────────────────────────────────────

class PDFReader:
    """
    Reads PDF files and extracts text as a flat list of lines.
    """

    def extract_text(self, pdf_path):
        """
        Extract all text lines from a PDF.

        Parameters:
            pdf_path (str | Path): Path to the PDF file.

        Returns:
            list[str]: Non-empty, stripped text lines.

        Raises:
            FileNotFoundError: If the file does not exist.

        Example:
            ["Login", "Username", "Password", "Forgot Password"]
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        extracted_lines = []

        try:
            document = fitz.open(pdf_path)

            for page in document:
                # get_text() returns the full page text as a string.
                # We split on newlines and strip whitespace from each line.
                raw_text = page.get_text()

                for line in raw_text.splitlines():
                    cleaned = line.strip()
                    if cleaned:  # skip blank lines
                        extracted_lines.append(cleaned)

            document.close()

        except Exception as error:
            print(f"[PDFReader] Error reading '{pdf_path}': {error}")
            return []

        return extracted_lines


# ── Quick Test ────────────────────────────────────────────────────────────

if __name__ == "__main__":

    reader = PDFReader()

    # Change this path to any PDF in your uploads folder to test.
    sample_pdf = "uploads/old/sample.pdf"

    try:
        lines = reader.extract_text(sample_pdf)

        print(f"\n📄 Extracted {len(lines)} lines from '{sample_pdf}'")
        print("─" * 40)

        for i, line in enumerate(lines, start=1):
            print(f"  {i:>3}. {line}")

        print()

    except FileNotFoundError as e:
        print(f"Error: {e}")