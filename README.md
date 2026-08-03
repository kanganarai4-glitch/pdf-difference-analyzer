# PDF Difference Analyzer

A Flask-based application that compares two folder uploads of PDF files and generates a detailed folder-level report in both CSV and Excel formats.

## Overview

This project is designed to compare an "old" version of a PDF folder against a "new" version. It inspects the PDF contents and structured fields, then classifies every file into one of four categories:

- `ADDED` — file only exists in the new folder
- `DELETED` — file only exists in the old folder
- `MODIFIED` — file exists in both folders, but attribute values differ
- `IDENTICAL` — file exists in both folders and attributes match

The generated report includes per-file comparison details and a human-readable difference summary.

## End-to-End Workflow

1. User opens the web UI at `/`.
2. User selects two folders using the folder upload controls:
   - one for the old PDF set
   - one for the new PDF set
3. The browser sends all PDF files from both folders to the backend via `/upload`.
4. The backend saves the files under `uploads/old/` and `uploads/new/`.
5. The frontend calls `/compare` to start the comparison.
6. The backend scans both upload folders recursively for PDFs.
7. Each PDF is parsed for structured attributes using `pdf_reader.py`.
8. The backend aligns records by `Order_ID`, or by relative filename when `Order_ID` is missing.
9. Differences are detected and written to:
   - `reports/difference_report.csv`
   - `reports/difference_report.xlsx`
10. The user can download the generated CSV report from the UI.

## Specifications

### Upload Behavior

- Files are accepted only if they end with `.pdf`.
- The relative folder structure from the upload is preserved when saving to `uploads/old/` and `uploads/new/`.
- Existing uploaded files are cleared before new uploads are saved, except files locked by another process.

### Folder Scan Logic

- `scanner.py` recursively scans each folder for files matching `*.pdf`.
- Each file key is stored as the relative path under the selected root folder.
- This means `uploads/old/Report/Invoice.pdf` and `uploads/new/Report/Invoice.pdf` are matched by relative path.

### PDF Parsing and Attribute Extraction

`pdf_reader.py` extracts all non-empty text lines from each PDF page using PyMuPDF.

It also attempts to parse the following structured fields from PDF text lines:

- `Order_ID`
- `Order_Date`
- `Customer_Name`
- `City`
- `State`
- `Region`
- `Country`
- `Category`
- `Sub_Category`
- `Product_Name`

The parser looks for labels such as `Order ID:`, `Customer Name:`, `City:`, etc. If expected labels are not found and there are enough lines, it may apply a positional fallback mapping.

### Comparison Rules

- Files present only in `old` are marked `DELETED`.
- Files present only in `new` are marked `ADDED`.
- Files present in both are compared by matching `Order_ID` first, then by relative path if `Order_ID` is absent.
- For common files, each structured field is compared and any change is recorded.
- If any field differs, the record is marked `MODIFIED`.
- If all parsed fields are equal, the record is marked `IDENTICAL`.

### Report Output Format

Both report files include these columns:

- `Comparison_Status`
- `Order_ID`
- `Order_Date`
- `Customer_Name`
- `City`
- `State`
- `Region`
- `Country`
- `Category`
- `Sub_Category`
- `Product_Name`
- `Difference_Details`

`Difference_Details` contains a summary such as:
- `Order was added.`
- `Order was deleted.`
- `Order_Date changed from '2024-06-01' to '2024-06-05'`
- `No differences detected.`

### Excel Report Styling

The spreadsheet created by `report_generator.py` includes:

- A title row with the compared folder names
- A timestamp row for the analysis
- Colored row highlights for `ADDED`, `DELETED`, and `MODIFIED` records
- Bold font for key columns such as `Comparison_Status` and `Order_ID`
- Column width auto-sizing for readability

## Project Structure

- `app.py` — Flask application, routes, upload handling, compare workflow, and report download endpoints
- `scanner.py` — Recursively finds PDFs and computes added/deleted/common file sets
- `pdf_reader.py` — Reads PDF text and extracts structured order/product fields
- `comparator.py` — Compares line-level text and builds diff structures for PDF content
- `report_generator.py` — Coordinates folder analysis and exports CSV/XLSX reports
- `templates/index.html` — UI markup for folder selection, status, and download actions
- `static/script.js` — Frontend upload flow, folder validation, and comparison requests
- `static/style.css` — Visual styling for the web interface
- `uploads/old/` and `uploads/new/` — temporary saved PDF uploads
- `reports/` — output report files generated after comparison

## Installation

1. Open PowerShell in the project folder.
2. Create a virtual environment:

```powershell
python -m venv venv
```

3. Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

4. Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

Start the Flask app:

```powershell
python app.py
```

Open your browser at:

```text
http://127.0.0.1:5000
```

## Usage Steps

1. Click the `OLD` upload area and choose a folder containing the previous version of your PDFs.
2. Click the `NEW` upload area and choose a folder containing the updated PDFs.
3. Confirm that both folder selectors show PDF counts.
4. Click `Compare PDFs`.
5. Wait for the status message to show results.
6. Download the generated CSV report using the provided link.

## Example Specifications

- Use `.pdf` files only.
- Folder upload preserves nested subfolders.
- Comparison is based on PDF content and extracted order attributes.
- Output files are written to `reports/difference_report.csv` and `reports/difference_report.xlsx`.

## Troubleshooting

- If no report is generated, ensure both folders were uploaded successfully.
- Check the console output if PDF parsing fails for a specific file.
- Confirm the virtual environment has `pymupdf`, `flask`, and `openpyxl` installed.

## Notes

- This tool is intended for comparing structured PDF data such as orders, invoices, or product sheets.
- It is not a full visual PDF diff tool; it compares extracted text and parsed fields.
- If a PDF is malformed or unreadable, the system logs the error and continues processing other files.

## License

This repository is provided as-is for internal or experimental use.
