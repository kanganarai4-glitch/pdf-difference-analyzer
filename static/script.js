const form = document.getElementById("uploadForm");

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const oldFiles = document.getElementById("oldFolder").files;
    const newFiles = document.getElementById("newFolder").files;

    if (oldFiles.length === 0 || newFiles.length === 0) {
        alert("Please select both folders.");
        return;
    }

    const formData = new FormData();

    // Adds the old PDFs
    for (const file of oldFiles) {
        formData.append("old_files", file, file.webkitRelativePath);
    }

    // Adds the  new PDFs
    for (const file of newFiles) {
        formData.append("new_files", file, file.webkitRelativePath);
    }

    document.getElementById("status").textContent = "Uploading folders...";

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const result = await response.json();

    document.getElementById("status").textContent = result.message;

});