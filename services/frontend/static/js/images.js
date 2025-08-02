// storage.js

window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.images-container');
  const currentPageSpan = document.getElementById('currentPage');
  const totalPagesSpan = document.getElementById('totalPages');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');
  const perPageSelect = document.getElementById('perPageSelect');

  function getQueryParam(name, defaultValue) {
    const params = new URLSearchParams(window.location.search);
    return parseInt(params.get(name)) || defaultValue;
  }

  function updateURL(page, perPage) {
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    params.set('per_page', perPage);
    history.replaceState(null, '', `${window.location.pathname}?${params}`);
  }

  function saveSettings(page, perPage) {
    localStorage.setItem('page', page.toString());
    localStorage.setItem('per_page', perPage.toString());
  }

  function loadSettings() {
    return {
      page: parseInt(localStorage.getItem('page')) || 1,
      perPage: parseInt(localStorage.getItem('per_page')) || 8
    };
  }

  function fetchImages(page = 1, perPage = 8) {
    saveSettings(page, perPage);
    updateURL(page, perPage);
    container.innerHTML = '';

    fetch(`/api/images/?page=${page}&per_page=${perPage}`)
      .then(response => response.json())
      .then(data => {
        const { files, total_pages } = data;

        if (total_pages > 0 && page > total_pages) {
          fetchImages(total_pages, perPage);
          return;
        }

        currentPageSpan.textContent = page;
        totalPagesSpan.textContent = total_pages;

        prevBtn.disabled = page <= 1;
        nextBtn.disabled = page >= total_pages;

        if (!files || files.length === 0) {
          const blankMessage = document.createElement('div');
          blankMessage.classList.add('blank-page');
          blankMessage.innerHTML = `<p>No images uploaded yet.</p>`;
          container.appendChild(blankMessage);
          return;
        }

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

            fetch(`/api/images/${encodeURIComponent(file)}`, { method: 'DELETE' })
              .then(response => {
                if (response.ok) {
                  fetchImages(page, perPage);
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
          [fileNameDiv, fileIconImg].forEach(el => {
            el.addEventListener('click', () => {
              window.location.href = `/images/${encodeURIComponent(file)}`;
            });
          });
        });
      });
  }

  const saved = loadSettings();

  let page = getQueryParam('page', saved.page);
  let perPage = getQueryParam('per_page', saved.perPage);

  perPageSelect.value = perPage.toString();
  updateURL(page, perPage);

  fetchImages(page, perPage);

  prevBtn.addEventListener('click', () => {
    if (page > 1) {
      page--;
      fetchImages(page, perPage);
    }
  });

  nextBtn.addEventListener('click', () => {
    page++;
    fetchImages(page, perPage);
  });

  perPageSelect.addEventListener('change', () => {
    perPage = parseInt(perPageSelect.value);
    page = 1;
    fetchImages(page, perPage);
  });
});
