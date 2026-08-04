

import fitz  # PyMuPDF — pip install pymupdf
from pathlib import Path


# ── PDFReader ─────────────────────────────────────────────────────────────

class PDFReader:
   

    def extract_text(self, pdf_path):
      

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

    def extract_attributes(self, pdf_path):
        """
        Extract structured order/product attributes from a PDF file.
        """
        lines = self.extract_text(pdf_path)
        
        data = {
            "Order_ID": "",
            "Order_Date": "",
            "Customer_Name": "",
            "City": "",
            "State": "",
            "Region": "",
            "Country": "",
            "Category": "",
            "Sub_Category": "",
            "Product_Name": ""
        }
        
        import re
        patterns = {
            "Order_ID": r"(?:order[-_\s]?id|order\s*(?:no|#))[:\-\s]+(.*)",
            "Order_Date": r"(?:order[-_\s]?date|date)[:\-\s]+(.*)",
            "Customer_Name": r"(?:customer[-_\s]?name|customer)[:\-\s]+(.*)",
            "City": r"(?:city)[:\-\s]+(.*)",
            "State": r"(?:state)[:\-\s]+(.*)",
            "Region": r"(?:region)[:\-\s]+(.*)",
            "Country": r"(?:country)[:\-\s]+(.*)",
            "Category": r"(?:category)[:\-\s]+(.*)",
            "Sub_Category": r"(?:sub[-_\s]?category)[:\-\s]+(.*)",
            "Product_Name": r"(?:product[-_\s]?name|product)[:\-\s]+(.*)"
        }
        
        matched_keys = set()
        for line in lines:
            for key, pattern in patterns.items():
                if key in matched_keys:
                    continue
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    data[key] = match.group(1).strip()
                    matched_keys.add(key)
                    
        has_colons = any(":" in line or "-" in line for line in lines)
        if not has_colons and len(lines) >= 10:
            keys_list = list(data.keys())
            for idx, key in enumerate(keys_list):
                if idx < len(lines):
                    data[key] = lines[idx].strip()
                    
        return data


if __name__ == "__main__":

    reader = PDFReader()

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