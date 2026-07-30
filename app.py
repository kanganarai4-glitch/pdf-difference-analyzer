"""
app.py

Flask web application entry point.
Handles HTTP requests from the browser.

Milestones covered:
    Milestone 1 — Project Setup  (Flask app running)
    Milestone 2 — User Interface (serves index.html)
    Milestone 3 — Folder Upload  (saves uploaded PDFs)
    Milestone 8 — Integration    (compare endpoint & file downloads)
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from report_generator import ReportGenerator

app = Flask(__name__)

# ── Folder paths ──────────────────────────────────────────────────────────
OLD_UPLOAD = Path("uploads/old")
NEW_UPLOAD = Path("uploads/new")
REPORTS_DIR = Path("reports")


# ── Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """
    Receive two folder uploads from the browser form.

    Expects:
        old_files — PDFs from the old folder
        new_files — PDFs from the new folder

    Saves them to:
        uploads/old/
        uploads/new/

    Preserves subfolder structure using webkitRelativePath.
    """

    try:
        # Clear old uploads before saving new ones
        # Skip files that are locked/open by another process (Windows)
        for folder in [OLD_UPLOAD, NEW_UPLOAD]:
            if folder.exists():
                for file in folder.rglob("*"):
                    if file.is_file():
                        try:
                            file.unlink()
                        except PermissionError:
                            pass  # File is in use, skip it

        OLD_UPLOAD.mkdir(parents=True, exist_ok=True)
        NEW_UPLOAD.mkdir(parents=True, exist_ok=True)

        # Save old folder PDFs
        old_files = request.files.getlist("old_files")
        for file in old_files:
            if file.filename.lower().endswith(".pdf"):
                save_path = OLD_UPLOAD / file.filename
                save_path.parent.mkdir(parents=True, exist_ok=True)
                file.save(save_path)

        # Save new folder PDFs
        new_files = request.files.getlist("new_files")
        for file in new_files:
            if file.filename.lower().endswith(".pdf"):
                save_path = NEW_UPLOAD / file.filename
                save_path.parent.mkdir(parents=True, exist_ok=True)
                file.save(save_path)

        return jsonify({
            "message": f"Uploaded {len(old_files)} old file(s) and {len(new_files)} new file(s) successfully."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/compare", methods=["POST"])
def compare():
    """
    Run the folder comparison and generate difference reports in XLSX and CSV.
    """
    try:
        if not OLD_UPLOAD.exists() or not NEW_UPLOAD.exists():
            return jsonify({"error": "Uploaded folders not found. Please upload folders first."}), 400

        generator = ReportGenerator()
        analysis = generator.analyze_differences(OLD_UPLOAD, NEW_UPLOAD)

        # Ensure reports directory exists
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        xlsx_path = REPORTS_DIR / "difference_report.xlsx"
        csv_path = REPORTS_DIR / "difference_report.csv"

        # Generate both report formats
        generator.generate_xlsx_report(analysis, xlsx_path)
        generator.generate_csv_report(analysis, csv_path)

        summary = {
            "added": len(analysis["added_files"]),
            "deleted": len(analysis["deleted_files"]),
            "modified": len(analysis["modified_files"]),
            "identical": len(analysis["identical_files"]),
        }

        return jsonify({
            "message": "Comparison completed successfully.",
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/xlsx")
def download_xlsx():
    """
    Serve the generated Excel report.
    """
    xlsx_path = REPORTS_DIR / "difference_report.xlsx"
    if not xlsx_path.exists():
        return jsonify({"error": "Report not found. Please run the comparison first."}), 404
    return send_file(xlsx_path, as_attachment=True, download_name="pdf_difference_report.xlsx")


@app.route("/download/csv")
def download_csv():
    """
    Serve the generated CSV report.
    """
    csv_path = REPORTS_DIR / "difference_report.csv"
    if not csv_path.exists():
        return jsonify({"error": "Report not found. Please run the comparison first."}), 404
    return send_file(csv_path, as_attachment=True, download_name="pdf_difference_report.csv")


# ── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)