document.addEventListener('DOMContentLoaded', () => {
      // 1. Category Filter Pill Clicking Interaction
      const categoryChips = document.querySelectorAll('#categoryChips .filter-pill');
      categoryChips.forEach(chip => {
        chip.addEventListener('click', () => {
          categoryChips.forEach(c => {
            c.classList.remove('bg-surface-dark', 'text-on-tertiary', 'font-semibold');
            c.classList.add('bg-surface-card', 'text-text-muted', 'border', 'border-border-subtle');
          });
          chip.classList.remove('bg-surface-card', 'text-text-muted', 'border', 'border-border-subtle');
          chip.classList.add('bg-surface-dark', 'text-on-tertiary', 'font-semibold');
        });
      });

      // 2. Client-side Article Search & Filter Simulator
      const searchInput = document.getElementById('articleSearchInput');
      const clearBtn = document.getElementById('clearSearchBtn');
      const articles = document.querySelectorAll('.article-card');
      const emptyState = document.getElementById('emptySearchState');
      const grid = document.getElementById('articlesGrid');

      function filterArticles() {
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        if (query.length > 0) {
          clearBtn.classList.remove('hidden');
        } else {
          clearBtn.classList.add('hidden');
        }

        articles.forEach(article => {
          const text = article.textContent.toLowerCase();
          if (text.includes(query)) {
            article.style.display = 'flex';
            visibleCount++;
          } else {
            article.style.display = 'none';
          }
        });

        if (visibleCount === 0) {
          emptyState.classList.remove('hidden');
          grid.classList.add('hidden');
        } else {
          emptyState.classList.add('hidden');
          grid.classList.remove('hidden');
        }
      }

      searchInput.addEventListener('input', filterArticles);

      clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        filterArticles();
        searchInput.focus();
      });

      // Reset filters button inside empty state
      document.getElementById('resetSearchFiltersBtn').addEventListener('click', () => {
        searchInput.value = '';
        filterArticles();
      });

      // 3. Testing Simulator Controls
      const toggleEmptyBtn = document.getElementById('toggleEmptyStateBtn');
      const resetViewBtn = document.getElementById('resetViewBtn');

      toggleEmptyBtn.addEventListener('click', () => {
        articles.forEach(a => a.style.display = 'none');
        grid.classList.add('hidden');
        emptyState.classList.remove('hidden');
      });

      resetViewBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.classList.add('hidden');
        articles.forEach(a => a.style.display = 'flex');
        grid.classList.remove('hidden');
        emptyState.classList.add('hidden');
      });
    });
