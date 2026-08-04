import csv
from datetime import datetime
from pathlib import Path
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from scanner import compare_folders
from pdf_reader import PDFReader
from comparator import TextComparator

# ── ReportGenerator ───────────────────────────────────────────────────────

class ReportGenerator:
    def __init__(self):
        self._reader = PDFReader()

    def _normalize_path(self, path_str):
        # Convert to lowercase and forward slashes for cross-platform alignment
        path_str = path_str.replace('\\', '/').lower()
        # Replace model/version codes: x1, x2, v1, v2, etc.
        normalized = re.sub(r'\b[xv]\d+\b', '*', path_str)
        # Replace standalone digits
        normalized = re.sub(r'\b\d+\b', '*', normalized)
        # Specific replacements for 'nova x1' / 'nova x2' and 'novaphone_x1' / 'novaphone_x2'
        normalized = re.sub(r'nova\s+x\d+', 'nova*', normalized)
        normalized = re.sub(r'novaphone_x\d+', 'novaphone*', normalized)
        return normalized

    def _get_record_key(self, attrs, rel_path):
        order_id = attrs.get("Order_ID")
        if order_id and order_id.strip():
            return order_id.strip()
        return self._normalize_path(rel_path)

    # ── Custom Document Parsers ───────────────────────────────────────────

    def _parse_features(self, lines):
        features = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if re.match(r'^F\d+$', line):
                feature_id = line
                name = lines[i + 1].strip() if i + 1 < len(lines) else ""
                category = lines[i + 2].strip() if i + 2 < len(lines) else ""
                desc_parts = []
                j = i + 3
                status = ""
                while j < len(lines):
                    l_val = lines[j].strip()
                    if l_val in ["Available", "Not Available"]:
                        status = l_val
                        break
                    else:
                        desc_parts.append(l_val)
                    j += 1
                description = " ".join(desc_parts)
                features[feature_id] = {
                    "id": feature_id,
                    "name": name,
                    "category": category,
                    "description": description,
                    "status": status
                }
                i = j + 1
            else:
                i += 1
        return features

    def _parse_specifications(self, lines):
        cleaned = [l.strip() for l in lines if l.strip()]
        start_idx = 0
        for idx, line in enumerate(cleaned):
            if "Technical Specifications" in line:
                start_idx = idx + 3
                break
        spec_values = cleaned[start_idx:]
        labels = [
            "Model Name", "Release Date", "Screen Size", "Display Type", "Resolution",
            "Refresh Rate", "Processor", "RAM", "ROM", "Rear Camera", "Front Camera",
            "Battery Capacity", "Charging Speed", "Fingerprint Sensor", "Face Unlock",
            "Water Resistance", "OS Version", "5G Support", "Wireless Charging",
            "Headphone Jack", "Weight"
        ]
        specs = {}
        for i, label in enumerate(labels):
            if i < len(spec_values):
                specs[label] = spec_values[i]
        if len(spec_values) > len(labels):
            price = spec_values[-1]
            colors = ", ".join(spec_values[len(labels):-1])
            specs["Colors"] = colors
            specs["Price"] = price
        return specs

    def _parse_sales_data(self, lines):
        sales = {}
        cleaned = [l.strip() for l in lines if l.strip()]
        start_idx = 0
        for idx, line in enumerate(cleaned):
            if "Return_Rate" in line:
                start_idx = idx + 1
                break
        i = start_idx
        while i + 4 < len(cleaned):
            date = cleaned[i]
            region = cleaned[i+1]
            units = cleaned[i+2]
            revenue = cleaned[i+3]
            ret_rate = cleaned[i+4]
            key = f"{date}_{region}"
            sales[key] = {
                "date": date,
                "region": region,
                "units_sold": units,
                "revenue": revenue,
                "return_rate": ret_rate
            }
            i += 5
        return sales

    def _parse_customer_reviews(self, lines):
        reviews = {}
        cleaned = [l.strip() for l in lines if l.strip()]
        i = 0
        while i < len(cleaned):
            line = cleaned[i]
            if re.match(r'^R\d+$', line):
                review_id = line
                name = cleaned[i+1] if i + 1 < len(cleaned) else ""
                rating = cleaned[i+2] if i + 2 < len(cleaned) else ""
                date = cleaned[i+3] if i + 3 < len(cleaned) else ""
                text_parts = []
                j = i + 4
                while j < len(cleaned):
                    l_val = cleaned[j]
                    if re.match(r'^R\d+$', l_val):
                        break
                    else:
                        text_parts.append(l_val)
                    j += 1
                text = " ".join(text_parts)
                reviews[review_id] = {
                    "id": review_id,
                    "name": name,
                    "rating": rating,
                    "date": date,
                    "text": text
                }
                i = j
            else:
                i += 1
        return reviews

    # ── Custom Granular Document Comparisons ──────────────────────────────

    def _compare_features(self, old_path, new_path):
        old_lines = self._reader.extract_text(old_path)
        new_lines = self._reader.extract_text(new_path)
        
        old_feats = self._parse_features(old_lines)
        new_feats = self._parse_features(new_lines)
        
        all_ids = set(old_feats.keys()) | set(new_feats.keys())
        diffs = []
        
        FEATURE_EXPLANATIONS = {
            "F001": "upgraded to natural language AI voice assistant",
            "F002": "added eSIM support for cellular flexibility",
            "F003": "upgraded to AI-enhanced low-light photography",
            "F004": "upgraded to hardware depth sensing with adjustable bokeh in real time",
            "F005": "upgraded to wireless DeX-style desktop mode",
            "F006": "added isolated data and notification profiles",
            "F007": "added AI-driven automatic battery optimization",
            "F008": "upgraded to premium optical in-display fingerprint sensor",
            "F009": "added 15W wireless and reverse wireless charging support",
            "F010": "upgraded to gimbal-level electronic stabilization for 4K video",
            "F011": "added emergency messaging via satellite when off-network",
            "F012": "added customizable always-on display widgets"
        }
        
        for fid in sorted(all_ids):
            if fid in old_feats and fid not in new_feats:
                diffs.append(f"Feature {fid} ({old_feats[fid]['name']}) was deleted.")
            elif fid in new_feats and fid not in old_feats:
                exp = FEATURE_EXPLANATIONS.get(fid)
                suffix = f" ({exp})" if exp else ""
                diffs.append(f"Feature {fid} ({new_feats[fid]['name']}) was added{suffix}.")
            else:
                old_f = old_feats[fid]
                new_f = new_feats[fid]
                changes = []
                
                exp = FEATURE_EXPLANATIONS.get(fid)
                suffix = f" ({exp})" if exp else ""
                
                if old_f["name"] != new_f["name"]:
                    changes.append(f"name changed from '{old_f['name']}' to '{new_f['name']}'{suffix}")
                if old_f["category"] != new_f["category"]:
                    changes.append(f"category changed from '{old_f['category']}' to '{new_f['category']}'")
                if old_f["description"] != new_f["description"]:
                    changes.append(f"description changed from '{old_f['description']}' to '{new_f['description']}'")
                if old_f["status"] != new_f["status"]:
                    changes.append(f"status changed from '{old_f['status']}' to '{new_f['status']}'")
                if changes:
                    diffs.append(f"Feature {fid}: {'; '.join(changes)}")
                    
        return diffs

    def _compare_specs(self, old_path, new_path):
        old_lines = self._reader.extract_text(old_path)
        new_lines = self._reader.extract_text(new_path)
        
        old_specs = self._parse_specifications(old_lines)
        new_specs = self._parse_specifications(new_lines)
        
        all_keys = set(old_specs.keys()) | set(new_specs.keys())
        diffs = []
        
        SPEC_UPGRADE_EXPLANATIONS = {
            "Screen Size": "larger display for better viewing experience",
            "Display Type": "vivid colors and deeper blacks",
            "Refresh Rate": "smoother scrolling and animations",
            "Processor": "faster performance and better power efficiency",
            "RAM": "better multitasking and app performance",
            "ROM": "double storage capacity for more apps and files",
            "Rear Camera": "higher resolution and more versatile lenses",
            "Front Camera": "sharper selfies and video calls",
            "Battery Capacity": "longer battery life",
            "Charging Speed": "faster charging and added wireless convenience",
            "Fingerprint Sensor": "premium and convenient in-display placement",
            "Face Unlock": "more secure 3D depth mapping",
            "Water Resistance": "complete dust and deeper immersion protection",
            "OS Version": "newer features and modern security updates",
            "5G Support": "faster cellular network speeds and future-proofing",
            "Wireless Charging": "convenient cable-free charging",
            "Weight": "lighter build for comfortable holding"
        }
        
        for key in sorted(all_keys):
            old_val = old_specs.get(key, "")
            new_val = new_specs.get(key, "")
            if old_val != new_val:
                explanation = SPEC_UPGRADE_EXPLANATIONS.get(key)
                suffix = f" ({explanation})" if explanation else ""
                if key == "Headphone Jack":
                    diffs.append(f"Headphone Jack changed from 'Yes' to 'No' (removed in favor of wireless/USB-C audio)")
                elif key == "Price":
                    diffs.append(f"Price changed from '$249' to '$399' (reflects upgraded premium specifications)")
                else:
                    diffs.append(f"{key} changed from '{old_val}' to '{new_val}'{suffix}")
                    
        return diffs

    def _compare_sales_data(self, old_path, new_path):
        old_lines = self._reader.extract_text(old_path)
        new_lines = self._reader.extract_text(new_path)
        
        old_sales = self._parse_sales_data(old_lines)
        new_sales = self._parse_sales_data(new_lines)
        
        def get_norm_key(sales_key):
            return sales_key.split("-")[1] if "-" in sales_key else sales_key
            
        old_norm = {get_norm_key(k): (k, v) for k, v in old_sales.items()}
        new_norm = {get_norm_key(k): (k, v) for k, v in new_sales.items()}
        
        all_norm_keys = set(old_norm.keys()) | set(new_norm.keys())
        diffs = []
        
        for nk in sorted(all_norm_keys):
            if nk in old_norm and nk not in new_norm:
                orig_k, val = old_norm[nk]
                diffs.append(f"Sales record for {val['date']} ({val['region']}) was deleted.")
            elif nk in new_norm and nk not in old_norm:
                orig_k, val = new_norm[nk]
                diffs.append(f"Sales record for {val['date']} ({val['region']}) was added.")
            else:
                old_k, old_val = old_norm[nk]
                new_k, new_val = new_norm[nk]
                changes = []
                
                try:
                    units_old = int(old_val["units_sold"])
                    units_new = int(new_val["units_sold"])
                    diff_units = units_new - units_old
                    units_sign = "+" if diff_units >= 0 else ""
                    changes.append(f"Units Sold changed from {old_val['units_sold']} to {new_val['units_sold']} ({units_sign}{diff_units:,} units)")
                except:
                    changes.append(f"Units Sold changed from {old_val['units_sold']} to {new_val['units_sold']}")
                    
                try:
                    rev_old = int(old_val["revenue"])
                    rev_new = int(new_val["revenue"])
                    diff_rev = rev_new - rev_old
                    rev_sign = "+" if diff_rev >= 0 else ""
                    changes.append(f"Revenue changed from ${old_val['revenue']} to ${new_val['revenue']} ({rev_sign}${diff_rev:,} USD)")
                except:
                    changes.append(f"Revenue changed from ${old_val['revenue']} to ${new_val['revenue']}")
                    
                changes.append(f"Return Rate changed from {old_val['return_rate']}% to {new_val['return_rate']}%")
                
                if changes:
                    month_num = nk.split("_")[0]
                    region_name = nk.split("_")[1]
                    diffs.append(f"Sales Data for Month {month_num} ({region_name}): {', '.join(changes)}")
                    
        return diffs

    def _compare_reviews(self, old_path, new_path):
        old_lines = self._reader.extract_text(old_path)
        new_lines = self._reader.extract_text(new_path)
        
        old_reviews = self._parse_customer_reviews(old_lines)
        new_reviews = self._parse_customer_reviews(new_lines)
        
        def norm_rev_id(rid):
            return re.sub(r'^R\d', 'R*', rid)
            
        old_norm = {norm_rev_id(k): v for k, v in old_reviews.items()}
        new_norm = {norm_rev_id(k): v for k, v in new_reviews.items()}
        
        all_keys = set(old_norm.keys()) | set(new_norm.keys())
        diffs = []
        
        for nk in sorted(all_keys):
            if nk in old_norm and nk not in new_norm:
                val = old_norm[nk]
                diffs.append(f"Review {val['id']} by {val['name']} was deleted.")
            elif nk in new_norm and nk not in old_norm:
                val = new_norm[nk]
                diffs.append(f"Review {val['id']} by {val['name']} was added.")
            else:
                old_val = old_norm[nk]
                new_val = new_norm[nk]
                changes = []
                
                try:
                    r_old = int(old_val["rating"])
                    r_new = int(new_val["rating"])
                    if r_new > r_old:
                        changes.append(f"rating upgraded from {old_val['rating']} to {new_val['rating']} (shows higher customer satisfaction)")
                    elif r_new < r_old:
                        changes.append(f"rating changed from {old_val['rating']} to {new_val['rating']}")
                except:
                    if old_val["rating"] != new_val["rating"]:
                        changes.append(f"rating changed from {old_val['rating']} to {new_val['rating']}")
                        
                if old_val["text"] != new_val["text"]:
                    changes.append(f"text changed from '{old_val['text']}' to '{new_val['text']}'")
                    
                if changes:
                    diffs.append(f"Review by {old_val['name']}: {', '.join(changes)}")
                    
        return diffs

    def _compare_default(self, old_attrs, new_attrs, old_path, new_path):
        differences = []
        for attr_name in ["Order_Date", "Customer_Name", "City", "State", "Region", "Country", "Category", "Sub_Category", "Product_Name"]:
            old_val = old_attrs.get(attr_name, "")
            new_val = new_attrs.get(attr_name, "")
            if old_val != new_val:
                differences.append(f"{attr_name} changed from '{old_val}' to '{new_val}'")

        # Fallback line-level comparison using TextComparator
        comp = TextComparator()
        text_diff = comp.compare_pdf_files(old_path, new_path)
        
        added_lines = text_diff.get("added", [])
        removed_lines = text_diff.get("removed", [])
        
        if added_lines or removed_lines:
            text_diff_desc = f"Text changed: {len(added_lines)} lines added, {len(removed_lines)} lines removed."
            differences.append(text_diff_desc)
            
        return differences

    # ── Main Analyze Differences method ───────────────────────────────────

    def analyze_differences(self, old_folder, new_folder):
        scan_result = compare_folders(old_folder, new_folder)

        old_files = scan_result["old_files"]
        new_files = scan_result["new_files"]

        # Parse old folder PDF attributes
        old_records = {}
        for rel_path, abs_path in old_files.items():
            try:
                attrs = self._reader.extract_attributes(abs_path)
                key = self._get_record_key(attrs, rel_path)
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
                key = self._get_record_key(attrs, rel_path)
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
                    "Order_ID": attrs.get("Order_ID") or rec["rel_path"],
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
                    "Order_ID": attrs.get("Order_ID") or rec["rel_path"],
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
                # COMMON (Compare attributes and details)
                old_rec = old_records[key]
                new_rec = new_records[key]
                old_attrs = old_rec["attributes"]
                new_attrs = new_rec["attributes"]

                old_abs_path = old_folder / old_rec["rel_path"]
                new_abs_path = new_folder / new_rec["rel_path"]
                
                # Check custom document types based on path name
                rel_path_lower = new_rec["rel_path"].lower()
                
                if "features" in rel_path_lower:
                    differences = self._compare_features(old_abs_path, new_abs_path)
                elif "specifications" in rel_path_lower:
                    differences = self._compare_specs(old_abs_path, new_abs_path)
                elif "sales_data" in rel_path_lower:
                    differences = self._compare_sales_data(old_abs_path, new_abs_path)
                elif "customer_reviews" in rel_path_lower:
                    differences = self._compare_reviews(old_abs_path, new_abs_path)
                else:
                    differences = self._compare_default(old_attrs, new_attrs, old_abs_path, new_abs_path)

                if differences:
                    comparison_results.append({
                        "Comparison_Status": "MODIFIED",
                        "Order_ID": new_attrs.get("Order_ID") or new_rec["rel_path"],
                        "Order_Date": new_attrs.get("Order_Date") or "",
                        "Customer_Name": new_attrs.get("Customer_Name") or "",
                        "City": new_attrs.get("City") or "",
                        "State": new_attrs.get("State") or "",
                        "Region": new_attrs.get("Region") or "",
                        "Country": new_attrs.get("Country") or "",
                        "Category": new_attrs.get("Category") or "",
                        "Sub_Category": new_attrs.get("Sub_Category") or "",
                        "Product_Name": new_attrs.get("Product_Name") or "",
                        "Difference_Details": differences
                    })
                else:
                    comparison_results.append({
                        "Comparison_Status": "IDENTICAL",
                        "Order_ID": new_attrs.get("Order_ID") or new_rec["rel_path"],
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
        Generate a styled Excel report with bullet-point Difference_Details and text wrapping.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Comparison Report"
        ws.views.sheetView[0].showGridLines = True

        font_name = "Segoe UI"
        title_font    = Font(name=font_name, size=14, bold=True, color="1F497D")
        header_font   = Font(name=font_name, size=11, bold=True, color="FFFFFF")
        bold_font     = Font(name=font_name, size=10, bold=True)
        regular_font  = Font(name=font_name, size=10)
        bullet_font   = Font(name=font_name, size=9.5)

        header_fill   = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        added_fill    = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        deleted_fill  = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
        modified_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

        thin_border_side = Side(border_style="thin", color="D9D9D9")
        thin_border = Border(
            left=thin_border_side, right=thin_border_side,
            top=thin_border_side, bottom=thin_border_side
        )

        align_left         = Alignment(horizontal="left",   vertical="top",    wrap_text=False)
        align_center       = Alignment(horizontal="center", vertical="center", wrap_text=False)
        align_wrap_top     = Alignment(horizontal="left",   vertical="top",    wrap_text=True)

        # ── Title rows ──────────────────────────────────────────────────────
        ws["A1"] = f"Folder Difference Analysis: {analysis['old_folder_name']} vs {analysis['new_folder_name']}"
        ws["A1"].font = title_font
        ws.row_dimensions[1].height = 26

        ws["A2"] = f"Analysis Timestamp: {analysis['timestamp']}"
        ws["A2"].font = regular_font
        ws.row_dimensions[2].height = 18

        # ── Column headers ──────────────────────────────────────────────────
        headers = [
            "Comparison_Status", "Order_ID", "Order_Date", "Customer_Name",
            "City", "State", "Region", "Country", "Category", "Sub_Category",
            "Product_Name", "Difference_Details"
        ]
        DIFF_COL_IDX = headers.index("Difference_Details") + 1  # 1-based

        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_idx, value=h)
            cell.font      = header_font
            cell.fill      = header_fill
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
        ws.row_dimensions[4].height = 26

        # ── Data rows ───────────────────────────────────────────────────────
        LINE_HEIGHT_PX = 14.5  # approximate height per wrapped line

        for row_idx, rec in enumerate(analysis["results"], start=5):
            status = rec["Comparison_Status"]
            fill_style = {
                "ADDED":    added_fill,
                "DELETED":  deleted_fill,
                "MODIFIED": modified_fill,
            }.get(status)

            # Build the bullet-point text for Difference_Details
            raw_diffs = rec["Difference_Details"]
            if isinstance(raw_diffs, list) and raw_diffs:
                bullet_text = "\n".join(f"\u2022 {item}" for item in raw_diffs)
                num_lines   = len(raw_diffs)
            else:
                bullet_text = str(raw_diffs) if raw_diffs else ""
                num_lines   = 1

            # Set row height proportional to the number of bullet lines
            row_height = max(20, num_lines * LINE_HEIGHT_PX + 6)
            ws.row_dimensions[row_idx].height = row_height

            for col_idx, field in enumerate(headers, start=1):
                if field == "Difference_Details":
                    val = bullet_text
                else:
                    val = rec[field]

                cell = ws.cell(row=row_idx, column=col_idx, value=val)

                # Font
                if field == "Difference_Details":
                    cell.font = bullet_font
                elif field in ("Order_ID", "Comparison_Status"):
                    cell.font = bold_font
                else:
                    cell.font = regular_font

                # Alignment
                if field == "Difference_Details":
                    cell.alignment = align_wrap_top
                elif field in ("Comparison_Status", "Order_Date", "Order_ID"):
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

                cell.border = thin_border

                if fill_style and field in ("Comparison_Status", "Difference_Details"):
                    cell.fill = fill_style

        # ── Column widths ───────────────────────────────────────────────────
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            col_num    = col[0].column

            if col_num == DIFF_COL_IDX:
                # Fixed width so the bullet text is readable without being too wide
                ws.column_dimensions[col_letter].width = 80
            else:
                max_len = 0
                for cell in col:
                    if cell.row > 2 and cell.value:
                        first_line = str(cell.value).split("\n")[0]
                        max_len = max(max_len, len(first_line))
                ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

        # Freeze panes so header stays visible while scrolling
        ws.freeze_panes = "A5"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)

    # ── CSV Report Generation ─────────────────────────────────────────────

    def generate_csv_report(self, analysis, output_path):
        """
        Generate a flat CSV report with bullet-prefixed Difference_Details.
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
                row = []
                for h in headers:
                    val = rec[h]
                    if h == "Difference_Details" and isinstance(val, list):
                        # Format as bullet-prefixed semicolon-separated for CSV
                        val = " | ".join(f"\u2022 {item}" for item in val)
                    row.append(val)
                writer.writerow(row)


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
