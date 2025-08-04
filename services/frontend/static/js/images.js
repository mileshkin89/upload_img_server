// storage.js

window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.images-container');
  const currentPageSpan = document.getElementById('currentPage');
  const totalPagesSpan = document.getElementById('totalPages');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');
  const perPageSelect = document.getElementById('perPageSelect');
  const sortParamSelect = document.getElementById('sortParams');
  const sortValueSelect = document.getElementById('sortValue');

  // Шаблоны подписей по типу сортировки
  const SORT_VALUE_OPTIONS = {
    sort_age: [
      { value: 'desc', label: 'Newest First' },
      { value: 'asc', label: 'Oldest First' },
    ],
    sort_size: [
      { value: 'desc', label: 'Big First' },
      { value: 'asc', label: 'Little First' },
    ]
  };

  function updateSortValueOptions(sortParam, selectedValue) {
    sortValueSelect.innerHTML = '';
    SORT_VALUE_OPTIONS[sortParam].forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;
      if (opt.value === selectedValue) {
        option.selected = true;
      }
      sortValueSelect.appendChild(option);
    });
  }

  function getQueryParam(name, defaultValue) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name) || defaultValue;
  }

  function updateURL(page, perPage, sortParam, sortValue) {
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    params.set('per_page', perPage);
    params.set('sort_param', sortParam);
    params.set('sort_value', sortValue);
    history.replaceState(null, '', `${window.location.pathname}?${params}`);
  }

  function saveSettings({ page, perPage, sortParam, sortValue }) {
    localStorage.setItem('page', page.toString());
    localStorage.setItem('per_page', perPage.toString());
    localStorage.setItem('sort_param', sortParam);
    localStorage.setItem('sort_value', sortValue);
  }

  function loadSettings() {
    return {
      page: parseInt(localStorage.getItem('page')) || 1,
      perPage: parseInt(localStorage.getItem('per_page')) || 8,
      sortParam: localStorage.getItem('sort_param') || 'sort_age',
      sortValue: localStorage.getItem('sort_value') || 'desc'
    };
  }

  function fetchImages(page = 1, perPage = 8, sortParam = 'sort_age', sortValue = 'desc') {
    saveSettings({ page, perPage, sortParam, sortValue });
    updateURL(page, perPage, sortParam, sortValue);
    container.innerHTML = '';

    fetch(`/api/images/?page=${page}&per_page=${perPage}&sort_param=${sortParam}&sort_value=${sortValue}`)
      .then(response => response.json())
      .then(data => {
        const { files, total_pages } = data;

        if (total_pages > 0 && page > total_pages) {
          fetchImages(total_pages, perPage, sortParam, sortValue);
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
                  fetchImages(page, perPage, sortParam, sortValue);
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

  // === Начальная загрузка ===
  const saved = loadSettings();

  let page = parseInt(getQueryParam('page', saved.page));
  let perPage = parseInt(getQueryParam('per_page', saved.perPage));
  let sortParam = getQueryParam('sort_param', saved.sortParam);
  let sortValue = getQueryParam('sort_value', saved.sortValue);

  // Применить в select элементы
  perPageSelect.value = perPage.toString();
  sortParamSelect.value = sortParam;
  updateSortValueOptions(sortParam, sortValue); // ⚠️ обновляем подписи

  updateURL(page, perPage, sortParam, sortValue);
  fetchImages(page, perPage, sortParam, sortValue);

  // === Слушатели ===
  prevBtn.addEventListener('click', () => {
    if (page > 1) {
      page--;
      fetchImages(page, perPage, sortParam, sortValue);
    }
  });

  nextBtn.addEventListener('click', () => {
    page++;
    fetchImages(page, perPage, sortParam, sortValue);
  });

  perPageSelect.addEventListener('change', () => {
    perPage = parseInt(perPageSelect.value);
    page = 1;
    fetchImages(page, perPage, sortParam, sortValue);
  });

  sortParamSelect.addEventListener('change', () => {
    sortParam = sortParamSelect.value;
    sortValue = SORT_VALUE_OPTIONS[sortParam][0].value; // сброс к первому значению
    updateSortValueOptions(sortParam, sortValue);
    page = 1;
    fetchImages(page, perPage, sortParam, sortValue);
  });

  sortValueSelect.addEventListener('change', () => {
    sortValue = sortValueSelect.value;
    page = 1;
    fetchImages(page, perPage, sortParam, sortValue);
  });
});
