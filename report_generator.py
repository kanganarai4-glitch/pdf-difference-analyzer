"""
report_generator.py  —  Milestone 7

Responsible for:
    Generating a structured CSV and Excel (.xlsx) report based on comparing
    order/product PDFs inside two folders, aligning records by Order_ID,
    and outputting the exact attributes:
    Order_ID, Order_Date, Customer_Name, City, State, Region, Country, Category, Sub_Category, Product_Name.
"""

import csv
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from scanner import compare_folders
from pdf_reader import PDFReader


# ── ReportGenerator ───────────────────────────────────────────────────────

class ReportGenerator:
    """
    Analyzes compared folders and generates Excel (.xlsx) and CSV reports.
    """

    def __init__(self):
        self._reader = PDFReader()

    def analyze_differences(self, old_folder, new_folder):
        """
        Scan folders, parse PDF attributes, and perform attribute-level comparison
        aligning on Order_ID (falling back to relative path if blank).
        """
        scan_result = compare_folders(old_folder, new_folder)

        old_files = scan_result["old_files"]
        new_files = scan_result["new_files"]

        # Parse old folder PDF attributes
        old_records = {}
        for rel_path, abs_path in old_files.items():
            try:
                attrs = self._reader.extract_attributes(abs_path)
                key = attrs.get("Order_ID") or rel_path
                old_records[key] = {
                    "rel_path": rel_path,
                    "attributes": attrs
                }
            except Exception as e:
                print(f"Error parsing old PDF {abs_path}: {e}")

        # Parse new folder PDF attributes
        new_records = {}
        for rel_path, abs_path in new_files.items():
            try:
                attrs = self._reader.extract_attributes(abs_path)
                key = attrs.get("Order_ID") or rel_path
                new_records[key] = {
                    "rel_path": rel_path,
                    "attributes": attrs
                }
            except Exception as e:
                print(f"Error parsing new PDF {abs_path}: {e}")

        all_keys = set(old_records.keys()) | set(new_records.keys())
        comparison_results = []

        for key in sorted(all_keys):
            if key in old_records and key not in new_records:
                # DELETED
                rec = old_records[key]
                attrs = rec["attributes"]
                comparison_results.append({
                    "Comparison_Status": "DELETED",
                    "Order_ID": attrs.get("Order_ID") or key,
                    "Order_Date": attrs.get("Order_Date") or "",
                    "Customer_Name": attrs.get("Customer_Name") or "",
                    "City": attrs.get("City") or "",
                    "State": attrs.get("State") or "",
                    "Region": attrs.get("Region") or "",
                    "Country": attrs.get("Country") or "",
                    "Category": attrs.get("Category") or "",
                    "Sub_Category": attrs.get("Sub_Category") or "",
                    "Product_Name": attrs.get("Product_Name") or "",
                    "Difference_Details": "Order was deleted."
                })
            elif key in new_records and key not in old_records:
                # ADDED
                rec = new_records[key]
                attrs = rec["attributes"]
                comparison_results.append({
                    "Comparison_Status": "ADDED",
                    "Order_ID": attrs.get("Order_ID") or key,
                    "Order_Date": attrs.get("Order_Date") or "",
                    "Customer_Name": attrs.get("Customer_Name") or "",
                    "City": attrs.get("City") or "",
                    "State": attrs.get("State") or "",
                    "Region": attrs.get("Region") or "",
                    "Country": attrs.get("Country") or "",
                    "Category": attrs.get("Category") or "",
                    "Sub_Category": attrs.get("Sub_Category") or "",
                    "Product_Name": attrs.get("Product_Name") or "",
                    "Difference_Details": "Order was added."
                })
            else:
                # COMMON (Compare attributes)
                old_rec = old_records[key]
                new_rec = new_records[key]
                old_attrs = old_rec["attributes"]
                new_attrs = new_rec["attributes"]

                differences = []
                for attr_name in ["Order_Date", "Customer_Name", "City", "State", "Region", "Country", "Category", "Sub_Category", "Product_Name"]:
                    old_val = old_attrs.get(attr_name, "")
                    new_val = new_attrs.get(attr_name, "")
                    if old_val != new_val:
                        differences.append(f"{attr_name} changed from '{old_val}' to '{new_val}'")

                if differences:
                    comparison_results.append({
                        "Comparison_Status": "MODIFIED",
                        "Order_ID": new_attrs.get("Order_ID") or key,
                        "Order_Date": new_attrs.get("Order_Date") or "",
                        "Customer_Name": new_attrs.get("Customer_Name") or "",
                        "City": new_attrs.get("City") or "",
                        "State": new_attrs.get("State") or "",
                        "Region": new_attrs.get("Region") or "",
                        "Country": new_attrs.get("Country") or "",
                        "Category": new_attrs.get("Category") or "",
                        "Sub_Category": new_attrs.get("Sub_Category") or "",
                        "Product_Name": new_attrs.get("Product_Name") or "",
                        "Difference_Details": "; ".join(differences)
                    })
                else:
                    comparison_results.append({
                        "Comparison_Status": "IDENTICAL",
                        "Order_ID": new_attrs.get("Order_ID") or key,
                        "Order_Date": new_attrs.get("Order_Date") or "",
                        "Customer_Name": new_attrs.get("Customer_Name") or "",
                        "City": new_attrs.get("City") or "",
                        "State": new_attrs.get("State") or "",
                        "Region": new_attrs.get("Region") or "",
                        "Country": new_attrs.get("Country") or "",
                        "Category": new_attrs.get("Category") or "",
                        "Sub_Category": new_attrs.get("Sub_Category") or "",
                        "Product_Name": new_attrs.get("Product_Name") or "",
                        "Difference_Details": "No differences detected."
                    })

        return {
            "old_folder_name": Path(old_folder).name,
            "new_folder_name": Path(new_folder).name,
            "old_folder_path": str(Path(old_folder).resolve()),
            "new_folder_path": str(Path(new_folder).resolve()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": comparison_results
        }

    # ── Excel Report Generation ───────────────────────────────────────────

    def generate_xlsx_report(self, analysis, output_path):
        """
        Generate a styled Excel report corresponding to the compared attributes.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Comparison Report"
        ws.views.sheetView[0].showGridLines = True

        font_name = "Segoe UI"
        title_font = Font(name=font_name, size=14, bold=True, color="1F497D")
        header_font = Font(name=font_name, size=11, bold=True, color="FFFFFF")
        bold_font = Font(name=font_name, size=10, bold=True)
        regular_font = Font(name=font_name, size=10)

        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        added_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")  # soft green
        deleted_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")  # soft orange/red
        modified_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")  # soft yellow

        thin_border_side = Side(border_style="thin", color="D9D9D9")
        thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

        align_left = Alignment(horizontal="left", vertical="center")
        align_center = Alignment(horizontal="center", vertical="center")

        # Title
        ws["A1"] = f"Folder Difference Analysis: {analysis['old_folder_name']} vs {analysis['new_folder_name']}"
        ws["A1"].font = title_font
        ws.row_dimensions[1].height = 25

        ws["A2"] = f"Analysis Timestamp: {analysis['timestamp']}"
        ws["A2"].font = regular_font
        ws.row_dimensions[2].height = 18

        # Headers
        headers = [
            "Comparison_Status", "Order_ID", "Order_Date", "Customer_Name",
            "City", "State", "Region", "Country", "Category", "Sub_Category",
            "Product_Name", "Difference_Details"
        ]

        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_left
        ws.row_dimensions[4].height = 24

        # Data Rows
        for row_idx, rec in enumerate(analysis["results"], start=5):
            ws.row_dimensions[row_idx].height = 20

            status = rec["Comparison_Status"]
            fill_style = None
            if status == "ADDED":
                fill_style = added_fill
            elif status == "DELETED":
                fill_style = deleted_fill
            elif status == "MODIFIED":
                fill_style = modified_fill

            for col_idx, field in enumerate(headers, start=1):
                val = rec[field]
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = bold_font if field in ["Order_ID", "Comparison_Status"] else regular_font
                cell.border = thin_border
                cell.alignment = align_center if field in ["Comparison_Status", "Order_Date", "Order_ID"] else align_left

                if fill_style and field in ["Comparison_Status", "Difference_Details"]:
                    cell.fill = fill_style

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row > 2 and cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)

    # ── CSV Report Generation ─────────────────────────────────────────────

    def generate_csv_report(self, analysis, output_path):
        """
        Generate a flat CSV report containing the aligned PDF attributes.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        headers = [
            "Comparison_Status", "Order_ID", "Order_Date", "Customer_Name",
            "City", "State", "Region", "Country", "Category", "Sub_Category",
            "Product_Name", "Difference_Details"
        ]

        with open(output_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for rec in analysis["results"]:
                row = [rec[h] for h in headers]
                writer.writerow(row)


# ── Quick Test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing updated ReportGenerator...")
    generator = ReportGenerator()
    old_dir = Path("uploads/old")
    new_dir = Path("uploads/new")

    if old_dir.exists() and new_dir.exists():
        analysis = generator.analyze_differences(old_dir, new_dir)
        generator.generate_csv_report(analysis, "reports/difference_report.csv")
        print("CSV Report generated successfully.")
    else:
        print("Uploads folders do not exist. Test skipped.")
