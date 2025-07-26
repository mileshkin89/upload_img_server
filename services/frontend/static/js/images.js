// storage.js
window.addEventListener('DOMContentLoaded', () => {
  fetch('/api/images/')
    .then(response => response.json())
    .then(files => {
      const container = document.querySelector('.images-container');

      files.forEach(file => {
        const row = document.createElement('div');
        row.classList.add('table-row');

        row.innerHTML = `
          <div class="file-name">
            <a href="/images/${file}" class="file-link">
              <img src="/images/${file}" alt="icon" class="file-icon">
            </a>  
            <a href="/images/${file}" class="file-link">  
              <span>${file}</span>
            </a>
          </div>
          <div class="file-url">http://localhost/images/${file}</div>
          <div class="file-delete">
            <button class="delete-btn">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        `;

        row.querySelector('.delete-btn').addEventListener('click', () => {
          if (!confirm(`Delete file ${file}?`)) return;

          fetch(`/api/images/${encodeURIComponent(file)}`, {
            method: 'DELETE'
          })
          .then(response => {
            if (response.ok) {
              row.remove();
            } else {
              alert("Failed to delete file");
            }
          })
          .catch(err => {
            console.error("Delete error:", err);
            alert("Error deleting file");
          });
        });

        container.appendChild(row);

        const fileNameDiv = row.querySelector('.file-name');
        const fileIconImg = row.querySelector('.file-icon');

        // Клик на превью или на имя — переход на страницу просмотра
        [fileNameDiv, fileIconImg].forEach(el => {
          el.addEventListener('click', () => {
            window.location.href = `/images/${encodeURIComponent(file)}`;
          });
        });
      });
    });
});