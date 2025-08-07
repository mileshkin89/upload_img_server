/**
 * @file upload.js
 * @description
 * Handles image upload via file input and drag-and-drop.
 * Allows user to upload an image, get a sharable link, and copy it to the clipboard.
 */
window.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const resultInput = document.getElementById('resultLink');
    const copyBtn = document.getElementById('copyBtn');
    const dropArea = document.querySelector('.drop-area');

    if (!uploadBtn || !fileInput || !resultInput || !copyBtn || !dropArea) return;

    /**
     * Prevents default browser behavior for drag and drop events.
     * Applied to the drop area to allow custom file handling.
     */
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, e => e.preventDefault());
    });

    /**
     * Opens file selector dialog when upload button is clicked.
     */
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    /**
     * Handles file upload via Fetch API.
     * Validates file type and size before sending.
     *
     * @param {File} file - The image file to upload.
     */
    function handleFileUpload(file) {
        /** @type {HTMLElement | null} */
        const uploadText = document.querySelector('.upload-main-text, .upload-error');
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxFileSize = 5 * 1024 * 1024;

        const isValidType = allowedTypes.includes(file.type);
        const isValidSize = file.size <= maxFileSize;

        if (isValidType && isValidSize) {
            uploadText.classList.remove('upload-error', 'upload-main-text');
            uploadText.classList.add('upload-main-text');
            uploadText.textContent = 'File selected: ' + file.name;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.name);

            fetch('/api/upload/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) // Expect JSON with { filename: string }
            .then(data => {
                const link = `https://localhost/images/${data.filename}`;
                resultInput.value = link;
            })
            .catch(error => {
                alert("\n" + "Loading error: " + error);
                resultInput.value = '';
            });
        } else {
            uploadText.classList.remove('upload-error', 'upload-main-text');
            uploadText.classList.add('upload-error');
            uploadText.textContent = 'Upload failed';
            resultInput.value = '';
        }
    }

    /**
     * Triggers when a file is selected using the input.
     */
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) handleFileUpload(file);
        fileInput.value = ''; // Reset input so same file can be selected again
    });

    /**
     * Handles file drop onto the drop area.
     *
     * @param {DragEvent} e - The drop event.
     */
    dropArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    });

    /**
     * Copies the result link to clipboard and shows feedback.
     */
    copyBtn.addEventListener('click', async () => {
        const link = resultInput.value;
        await navigator.clipboard.writeText(link);

        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = 'COPY';
        }, 1500);
    });
});