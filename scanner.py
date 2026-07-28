"""
scanner.py  —  Milestone 4

Responsible for:
    1. Scanning a folder recursively for PDF files.
    2. Comparing two folders to find Added, Deleted, and Common PDFs.

How it works
─────────────────────────────────────────────────────────────────
  scan_folder("uploads/old")  →  {"Login.pdf": Path(...), ...}

  compare_folders("uploads/old", "uploads/new")  →  {
      "old_files": {...},
      "new_files": {...},
      "added":    ["Payment.pdf"],
      "deleted":  ["OldReport.pdf"],
      "common":   ["Login.pdf", "Dashboard.pdf"],
  }
"""

from pathlib import Path


# ── Public API ────────────────────────────────────────────────────────────

def scan_folder(folder_path):
    """
    Recursively scan a folder for PDF files.

    Parameters:
        folder_path (str | Path): Root folder to scan.

    Returns:
        dict[str, Path]:
            Keys   — relative path string, e.g. "Reports/Sales.pdf"
            Values — absolute Path object to the file

    Example:
        {
            "Login.pdf":         Path("uploads/old/Login.pdf"),
            "Reports/Sales.pdf": Path("uploads/old/Reports/Sales.pdf"),
        }
    """

    folder = Path(folder_path)

    if not folder.exists():
        return {}

    files = {}

    for pdf_file in folder.rglob("*.pdf"):
        # Make the key relative to the root folder so both
        # old and new folders share the same key namespace.
        relative_path = pdf_file.relative_to(folder)
        files[str(relative_path)] = pdf_file

    return files


def compare_folders(old_folder, new_folder):
    """
    Compare two folders and classify every PDF.

    Parameters:
        old_folder (str | Path): The original (old) folder.
        new_folder (str | Path): The updated (new) folder.

    Returns:
        dict with:
            old_files  — dict from scan_folder(old_folder)
            new_files  — dict from scan_folder(new_folder)
            added      — list of PDFs only in new folder
            deleted    — list of PDFs only in old folder
            common     — list of PDFs present in both folders
    """

    old_files = scan_folder(old_folder)
    new_files = scan_folder(new_folder)

    old_set = set(old_files.keys())
    new_set = set(new_files.keys())

    added   = sorted(new_set - old_set)   # in new, not in old
    deleted = sorted(old_set - new_set)   # in old, not in new
    common  = sorted(old_set & new_set)   # in both

    return {
        "old_files": old_files,
        "new_files": new_files,
        "added":     added,
        "deleted":   deleted,
        "common":    common,
    }


# ── Quick Test (run this file directly to verify) ─────────────────────────

if __name__ == "__main__":

    result = compare_folders("uploads/old", "uploads/new")

    print("\n📂 Added Files  (only in NEW folder)")
    print("─" * 40)
    for f in result["added"]:
        print(f"  + {f}")

    print("\n🗑️  Deleted Files  (only in OLD folder)")
    print("─" * 40)
    for f in result["deleted"]:
        print(f"  - {f}")

    print("\n📄 Common Files  (in both folders)")
    print("─" * 40)
    for f in result["common"]:
        print(f"  = {f}")

    print(f"\nTotal: {len(result['added'])} added, "
          f"{len(result['deleted'])} deleted, "
          f"{len(result['common'])} common.\n")