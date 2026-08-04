

from pathlib import Path


# ── Public API ────────────────────────────────────────────────────────────

def scan_folder(folder_path):

    folder = Path(folder_path)

    if not folder.exists():
        return {}

    files = {}

    for pdf_file in folder.rglob("*.pdf"):
        relative_path = pdf_file.relative_to(folder)
        files[str(relative_path)] = pdf_file

    return files


def compare_folders(old_folder, new_folder):
   

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