"""
comparator.py  —  Milestone 6

Responsible for:
    Comparing the text content of two versions of the same PDF
    and producing a structured diff (lines added, removed, unchanged).

How it works
─────────────────────────────────────────────────────────────────
  Uses Python's built-in difflib.SequenceMatcher to compare
  two lists of text lines (produced by PDFReader).

  compare_text(old_lines, new_lines)  →  {
      "added":     ["New button label", ...],
      "removed":   ["Old button label", ...],
      "unchanged": ["Login", "Username", ...],
      "diff":      [
          {"tag": "equal",   "line": "Login"},
          {"tag": "delete",  "line": "Old text"},
          {"tag": "insert",  "line": "New text"},
          ...
      ]
  }

  compare_pdf_files(old_path, new_path)  →  same structure above,
      but reads the PDFs automatically using PDFReader.

Example
─────────────────────────────────────────────────────────────────
  comp = TextComparator()
  result = comp.compare_pdf_files(
      "uploads/old/Login.pdf",
      "uploads/new/Login.pdf"
  )
  print(result["added"])    # lines only in new version
  print(result["removed"])  # lines only in old version
"""

import difflib
from pathlib import Path
from pdf_reader import PDFReader


# ── TextComparator ────────────────────────────────────────────────────────

class TextComparator:
    """
    Compares two lists of text lines and returns a structured diff.
    """

    def __init__(self):
        self._reader = PDFReader()

    # ── Public Methods ────────────────────────────────────────────────────

    def compare_text(self, old_lines, new_lines):
        """
        Compare two lists of text lines using SequenceMatcher.

        Parameters:
            old_lines (list[str]): Lines from the old version of the PDF.
            new_lines (list[str]): Lines from the new version of the PDF.

        Returns:
            dict:
                added     — list of lines only in new_lines
                removed   — list of lines only in old_lines
                unchanged — list of lines present in both
                diff      — ordered list of dicts, each with:
                                "tag"  : "equal" | "insert" | "delete"
                                "line" : the text of the line
        """

        matcher = difflib.SequenceMatcher(
            isjunk=None,
            a=old_lines,
            b=new_lines,
            autojunk=False,
        )

        added     = []
        removed   = []
        unchanged = []
        diff      = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            if tag == "equal":
                for line in old_lines[i1:i2]:
                    unchanged.append(line)
                    diff.append({"tag": "equal", "line": line})

            elif tag == "replace":
                # Treat replace as: delete old lines, then insert new lines
                for line in old_lines[i1:i2]:
                    removed.append(line)
                    diff.append({"tag": "delete", "line": line})
                for line in new_lines[j1:j2]:
                    added.append(line)
                    diff.append({"tag": "insert", "line": line})

            elif tag == "delete":
                for line in old_lines[i1:i2]:
                    removed.append(line)
                    diff.append({"tag": "delete", "line": line})

            elif tag == "insert":
                for line in new_lines[j1:j2]:
                    added.append(line)
                    diff.append({"tag": "insert", "line": line})

        return {
            "added":     added,
            "removed":   removed,
            "unchanged": unchanged,
            "diff":      diff,
        }

    def compare_pdf_files(self, old_path, new_path):
        """
        Read two PDF files and compare their text content.

        Parameters:
            old_path (str | Path): Path to the old PDF.
            new_path (str | Path): Path to the new PDF.

        Returns:
            dict: Same structure as compare_text(), plus:
                "old_path" — str path to the old file
                "new_path" — str path to the new file
                "error"    — error message string if reading fails, else None

        Example:
            comp = TextComparator()
            result = comp.compare_pdf_files(
                "uploads/old/Login.pdf",
                "uploads/new/Login.pdf"
            )
        """

        old_path = Path(old_path)
        new_path = Path(new_path)

        base_result = {
            "old_path": str(old_path),
            "new_path": str(new_path),
            "error":    None,
        }

        try:
            old_lines = self._reader.extract_text(old_path)
        except FileNotFoundError as e:
            return {**base_result, "error": str(e),
                    "added": [], "removed": [], "unchanged": [], "diff": []}

        try:
            new_lines = self._reader.extract_text(new_path)
        except FileNotFoundError as e:
            return {**base_result, "error": str(e),
                    "added": [], "removed": [], "unchanged": [], "diff": []}

        result = self.compare_text(old_lines, new_lines)
        return {**base_result, **result}


# ── Quick Test (run this file directly to verify) ─────────────────────────

if __name__ == "__main__":

    comp = TextComparator()

    # ── Example using plain text lists (no PDFs needed) ───────────────────
    old = ["Login", "Username", "Password", "Forgot Password", "Submit"]
    new = ["Login", "Email", "Password", "Remember Me", "Sign In"]

    result = comp.compare_text(old, new)

    print("\n--- Text Comparison Result ---")
    print("-" * 40)

    print("\nUnchanged lines:")
    for line in result["unchanged"]:
        print(f"   = {line}")

    print("\nAdded lines (only in NEW):")
    for line in result["added"]:
        print(f"   + {line}")

    print("\nRemoved lines (only in OLD):")
    for line in result["removed"]:
        print(f"   - {line}")

    print("\nFull Diff (in order):")
    print("-" * 40)
    symbols = {"equal": "=", "insert": "+", "delete": "-"}
    for entry in result["diff"]:
        sym = symbols.get(entry["tag"], "?")
        print(f"  [{sym}] {entry['line']}")

    print(f"\nSummary: {len(result['added'])} added, "
          f"{len(result['removed'])} removed, "
          f"{len(result['unchanged'])} unchanged.\n")
