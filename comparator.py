

import difflib
from pathlib import Path
from pdf_reader import PDFReader


# ── TextComparator ────────────────────────────────────────────────────────

class TextComparator:
    

    def __init__(self):
        self._reader = PDFReader()

    # ── Public Methods ────────────────────────────────────────────────────

    def compare_text(self, old_lines, new_lines):
        

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



if __name__ == "__main__":

    comp = TextComparator()

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
