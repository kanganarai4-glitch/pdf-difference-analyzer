"""
app.py

Flask web application entry point.
Handles HTTP requests from the browser.

Milestones covered:
    Milestone 1 — Project Setup  (Flask app running)
    Milestone 2 — User Interface (serves index.html)
    Milestone 3 — Folder Upload  (saves uploaded PDFs)
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path

app = Flask(__name__)

# ── Folder paths ──────────────────────────────────────────────────────────
OLD_UPLOAD = Path("uploads/old")
NEW_UPLOAD = Path("uploads/new")


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


# ── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)