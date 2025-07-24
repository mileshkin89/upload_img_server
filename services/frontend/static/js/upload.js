// upload.js
window.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const resultInput = document.getElementById('resultLink');
    const copyBtn = document.getElementById('copyBtn');
    const dropArea = document.querySelector('.drop-area');

    if (!uploadBtn || !fileInput || !resultInput || !copyBtn || !dropArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, e => e.preventDefault());
    });

    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    function handleFileUpload(file) {
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
            .then(response => response.json())  //  JSON with {"filename": "..."}
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

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) handleFileUpload(file);
        fileInput.value = '';
    });

    dropArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    });


    copyBtn.addEventListener('click', async () => {
        const link = resultInput.value;
        await navigator.clipboard.writeText(link);

        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = 'COPY';
        }, 1500);
    });
});

