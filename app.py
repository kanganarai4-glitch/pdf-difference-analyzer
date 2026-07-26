from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os

app = Flask(__name__)

OLD_UPLOAD = Path("uploads/old")
NEW_UPLOAD = Path("uploads/new")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    # Clear old uploads
    for folder in [OLD_UPLOAD, NEW_UPLOAD]:
        if folder.exists():
            for file in folder.rglob("*"):
                if file.is_file():
                    file.unlink()

    OLD_UPLOAD.mkdir(parents=True, exist_ok=True)
    NEW_UPLOAD.mkdir(parents=True, exist_ok=True)

    # Save old folder PDFs
    for file in request.files.getlist("old_files"):

        save_path = OLD_UPLOAD / file.filename

        save_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(save_path)

    # Save new folder PDFs
    for file in request.files.getlist("new_files"):

        save_path = NEW_UPLOAD / file.filename

        save_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(save_path)

    return jsonify({
        "message": "Folders uploaded successfully!"
    })


if __name__ == "__main__":
    app.run(debug=True)