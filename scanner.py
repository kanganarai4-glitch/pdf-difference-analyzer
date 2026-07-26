"""
scanner.py

Responsible for scanning PDF files recursively
and comparing the folder structure.
"""

from pathlib import Path


def scan_folder(folder_path):
    """
    Recursively scan a folder for PDF files.

    Returns:
        dict

        Example:

        {
            "Module1/Login.pdf": Path("uploads/old/Module1/Login.pdf"),
            "Reports/Sales.pdf": Path("uploads/old/Reports/Sales.pdf")
        }
    """

    folder = Path(folder_path)

    files = {}

    # Find every PDF recursively
    for pdf_file in folder.rglob("*.pdf"):

        # Convert absolute path into relative path
        relative_path = pdf_file.relative_to(folder)

        # Store in dictionary
        files[str(relative_path)] = pdf_file

    return files


def compare_folders(old_folder, new_folder):
    """
    Compare two folders.

    Returns:

    added_files
    deleted_files
    common_files
    """

    old_files = scan_folder(old_folder)
    new_files = scan_folder(new_folder)

    old_set = set(old_files.keys())
    new_set = set(new_files.keys())

    added = sorted(new_set - old_set)

    deleted = sorted(old_set - new_set)

    common = sorted(old_set & new_set)

    return {
        "old_files": old_files,
        "new_files": new_files,
        "added": added,
        "deleted": deleted,
        "common": common,
    }


if __name__ == "__main__":

    result = compare_folders(
        "uploads/old",
        "uploads/new"
    )

    print("\nAdded Files")
    print("--------------------")

    for file in result["added"]:
        print(file)

    print("\nDeleted Files")
    print("--------------------")

    for file in result["deleted"]:
        print(file)

    print("\nCommon Files")
    print("--------------------")

    for file in result["common"]:
        print(file)