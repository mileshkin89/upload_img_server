/**
 * Image Gallery Storage Script
 *
 * This module handles the image gallery logic:
 * - Fetching and displaying images with pagination and sorting
 * - Saving settings in localStorage and URL
 * - Deleting images
 * - Copying image URLs to clipboard
 *
 * Expected HTML structure includes elements with IDs:
 *   - #currentPage, #totalPages
 *   - #prevPage, #nextPage
 *   - #perPageSelect, #sortParams, #sortValue
 *   - .image-gallery container
 */

window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.image-gallery');
  const currentPageSpan = document.getElementById('currentPage');
  const totalPagesSpan = document.getElementById('totalPages');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');
  const perPageSelect = document.getElementById('perPageSelect');
  const sortParamSelect = document.getElementById('sortParams');
  const sortValueSelect = document.getElementById('sortValue');


  const SORT_VALUE_OPTIONS = {
    sort_age: [
      { value: 'desc', label: 'Newest First' },
      { value: 'asc', label: 'Oldest First' },
    ],
    sort_size: [
      { value: 'desc', label: 'Big First' },
      { value: 'asc', label: 'Little First' },
    ],
    sort_name: [
      { value: 'desc', label: ' Z - A ' },
      { value: 'asc', label: ' A - Z ' },
    ],
  };

  /**
   * Updates the sort direction dropdown based on selected sort param.
   * @param {string} sortParam - The selected sort parameter key.
   * @param {string} selectedValue - The current selected sort order.
   */
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

  /**
   * Retrieves query parameter from URL.
   * @param {string} name - Parameter name.
   * @param {any} defaultValue - Default value if not found.
   * @returns {string}
   */
  function getQueryParam(name, defaultValue) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name) || defaultValue;
  }

  /**
   * Updates the URL with current pagination and sorting state.
   */
  function updateURL(page, perPage, sortParam, sortValue) {
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    params.set('per_page', perPage);
    params.set('sort_param', sortParam);
    params.set('sort_value', sortValue);
    history.replaceState(null, '', `${window.location.pathname}?${params}`);
  }

  /**
   * Saves current pagination and sorting settings to localStorage.
   */
  function saveSettings({ page, perPage, sortParam, sortValue }) {
    localStorage.setItem('page', page.toString());
    localStorage.setItem('per_page', perPage.toString());
    localStorage.setItem('sort_param', sortParam);
    localStorage.setItem('sort_value', sortValue);
  }

  /**
   * Loads saved settings from localStorage.
   * @returns {{ page: number, perPage: number, sortParam: string, sortValue: string }}
   */
  function loadSettings() {
    return {
      page: parseInt(localStorage.getItem('page')) || 1,
      perPage: parseInt(localStorage.getItem('per_page')) || 8,
      sortParam: localStorage.getItem('sort_param') || 'sort_age',
      sortValue: localStorage.getItem('sort_value') || 'desc'
    };
  }

  /**
   * Fetches images from API and renders them.
   * @param {number} page
   * @param {number} perPage
   * @param {string} sortParam
   * @param {string} sortValue
   */
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
          const imageUrl = `http://localhost/images/${encodeURIComponent(file)}`;
          const card = document.createElement('div');
          card.classList.add('image-card');
          card.innerHTML = `
            <div class="image-card-preview">
              <a href="/images/${file}">
                <img src="/images/${file}" alt="${file}" loading="lazy" />
              </a>
            </div>
            <div class="image-card-info">
              <h3 class="image-card-title" title="${file}">${file}</h3>
              <p class="image-card-url" title="${imageUrl}">${imageUrl}</p>
              <div class="image-card-actions">
                <button class="copy-url-btn">Copy URL</button>
                <button class="card-delete-btn" aria-label="Delete image">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </div>
          `;

          // Copy image URL to clipboard
          const copyBtn = card.querySelector('.copy-url-btn');
          copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(imageUrl)
              .then(() => alert('Image URL copied to clipboard!'))
              .catch(err => {
                console.error('Copy failed:', err);
                alert('Failed to copy URL');
              });
          });

          // Delete image
          const deleteBtn = card.querySelector('.card-delete-btn');
          deleteBtn.addEventListener('click', () => {
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

          container.appendChild(card);
        });
      });
  }

  // Initialization
  const saved = loadSettings();

  let page = parseInt(getQueryParam('page', saved.page));
  let perPage = parseInt(getQueryParam('per_page', saved.perPage));
  let sortParam = getQueryParam('sort_param', saved.sortParam);
  let sortValue = getQueryParam('sort_value', saved.sortValue);

  perPageSelect.value = perPage.toString();
  sortParamSelect.value = sortParam;
  updateSortValueOptions(sortParam, sortValue);

  updateURL(page, perPage, sortParam, sortValue);
  fetchImages(page, perPage, sortParam, sortValue);

  // UI Listeners
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
    sortValue = SORT_VALUE_OPTIONS[sortParam][0].value;
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
