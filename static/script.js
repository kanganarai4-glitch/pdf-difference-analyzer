/**
 * script.js
 *
 * Handles folder selection display and form submission.
 * Currently wired to /upload (Milestone 3).
 * Will be extended to call /compare in Milestone 8.
 */

const form       = document.getElementById("uploadForm");
const oldInput   = document.getElementById("oldFolder");
const newInput   = document.getElementById("newFolder");
const oldInfo    = document.getElementById("oldFolderInfo");
const newInfo    = document.getElementById("newFolderInfo");
const oldZone    = document.getElementById("oldDropZone");
const newZone    = document.getElementById("newDropZone");
const compareBtn = document.getElementById("compareBtn");
const btnText    = document.getElementById("btnText");
const btnSpinner = document.getElementById("btnSpinner");
const statusArea = document.getElementById("statusArea");
const statusMsg  = document.getElementById("statusMessage");

// ── Folder selection feedback ──────────────────────────────────────────────

oldInput.addEventListener("change", () => {
    const count = filterPDFs(oldInput.files);
    oldInfo.textContent = count > 0
        ? `${count} PDF file(s) selected`
        : "No PDFs found in folder";
    oldZone.classList.toggle("active", count > 0);
});

newInput.addEventListener("change", () => {
    const count = filterPDFs(newInput.files);
    newInfo.textContent = count > 0
        ? `${count} PDF file(s) selected`
        : "No PDFs found in folder";
    newZone.classList.toggle("active", count > 0);
});

/** Return how many files in a FileList are PDFs */
function filterPDFs(fileList) {
    return Array.from(fileList).filter(f =>
        f.name.toLowerCase().endsWith(".pdf")
    ).length;
}

// ── Form submit ────────────────────────────────────────────────────────────

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const oldFiles = oldInput.files;
    const newFiles = newInput.files;

    // Validation
    if (oldFiles.length === 0 || newFiles.length === 0) {
        showStatus("Please select both folders before comparing.", "error");
        return;
    }

    if (filterPDFs(oldFiles) === 0 && filterPDFs(newFiles) === 0) {
        showStatus("No PDF files found in the selected folders.", "error");
        return;
    }

    // Build FormData
    const formData = new FormData();

    for (const file of oldFiles) {
        formData.append("old_files", file, file.webkitRelativePath || file.name);
    }

    for (const file of newFiles) {
        formData.append("new_files", file, file.webkitRelativePath || file.name);
    }

    // Show loading state
    setLoading(true);
    showStatus("Uploading folders...", "loading");

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            showStatus("✅ " + result.message, "success");
        } else {
            showStatus("❌ Upload failed: " + (result.error || "Unknown error"), "error");
        }

    } catch (err) {
        showStatus("❌ Network error: " + err.message, "error");
    } finally {
        setLoading(false);
    }

});

// ── Helpers ────────────────────────────────────────────────────────────────

function showStatus(message, type = "") {
    statusArea.classList.remove("hidden");
    statusMsg.textContent  = message;
    statusMsg.className    = "status-message " + type;
}

function setLoading(isLoading) {
    compareBtn.disabled = isLoading;
    btnText.classList.toggle("hidden", isLoading);
    btnSpinner.classList.toggle("hidden", !isLoading);
}