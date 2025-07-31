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
    history.pushState(null, '', `${window.location.pathname}?${params}`);
  }

  function fetchImages(page = 1, perPage = 8) {
    updateURL(page, perPage);
    container.innerHTML = '';

    fetch(`/api/images/?page=${page}&per_page=${perPage}`)
      .then(response => response.json())
      .then(data => {
        const { files, total_pages } = data;

        currentPageSpan.textContent = page;
        totalPagesSpan.textContent = total_pages;

        prevBtn.disabled = page <= 1;
        nextBtn.disabled = page >= total_pages;

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
                if (response.ok) row.remove();
                else alert("Failed to delete file");
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

  // Initial values from URL
  let page = getQueryParam('page', 1);
  let perPage = getQueryParam('per_page', parseInt(perPageSelect.value));

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
