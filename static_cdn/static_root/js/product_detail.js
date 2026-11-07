// Quantity Stepper
    let currentQty = 1;
    const qtyDisplay = document.getElementById('qty-display');

    function incrementQty() {
      if (currentQty < 10) {
        currentQty++;
        qtyDisplay.textContent = currentQty.toLocaleString('fa-IR');
      }
    }

    function decrementQty() {
      if (currentQty > 1) {
        currentQty--;
        qtyDisplay.textContent = currentQty.toLocaleString('fa-IR');
      }
    }

    // Color Swatch Selection
    function selectColor(buttonElement, colorName) {
      document.querySelectorAll('.color-swatch').forEach(btn => {
        btn.classList.remove('ring-2', 'ring-[#7628F5]', 'ring-offset-2');
        btn.innerHTML = '';
        btn.setAttribute('aria-checked', 'false');
      });
      buttonElement.classList.add('ring-2', 'ring-[#7628F5]', 'ring-offset-2');
      buttonElement.innerHTML = '<span class="material-symbols-outlined text-white text-[16px]">check</span>';
      buttonElement.setAttribute('aria-checked', 'true');
      document.getElementById('selected-color-label').textContent = colorName;
    }

    // Wishlist Toggle
    let isWishlisted = false;
    function toggleWishlist() {
      isWishlisted = !isWishlisted;
      const icon = document.getElementById('wishlist-icon');
      if (isWishlisted) {
        icon.classList.add('fill-icon', 'text-red-500');
        icon.style.fontVariationSettings = "'FILL' 1";
      } else {
        icon.classList.remove('fill-icon', 'text-red-500');
        icon.style.fontVariationSettings = "'FILL' 0";
      }
    }

    // Tab Switching
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
        content.classList.remove('block');
      });
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('text-[#7628F5]', 'border-[#7628F5]', 'font-bold');
        b.classList.add('text-text-muted', 'border-transparent', 'font-medium');
      });

      document.getElementById(tabId).classList.remove('hidden');
      document.getElementById(tabId).classList.add('block');
      btn.classList.add('text-[#7628F5]', 'border-[#7628F5]', 'font-bold');
      btn.classList.remove('text-text-muted', 'border-transparent', 'font-medium');
    }

    // Thumbnail Gallery Switcher
    function changeGallery(thumbBtn, index) {
      document.querySelectorAll('.thumbnail-item').forEach(item => {
        item.classList.remove('border-primary-container', 'border-2');
        item.classList.add('border-border-structural', 'border');
        const indicator = item.querySelector('.active-indicator');
        if (indicator) indicator.remove();
      });

      thumbBtn.classList.remove('border-border-structural', 'border');
      thumbBtn.classList.add('border-primary-container', 'border-2');
      
      const dot = document.createElement('span');
      dot.className = 'active-indicator absolute -bottom-1 w-6 h-1 rounded-full bg-accent-lime';
      thumbBtn.appendChild(dot);
    }

    // Add To Cart Micro-Feedback
    function addToCartAnimation() {
      const btn = document.getElementById('add-to-cart-cta');
      const originalHTML = btn.innerHTML;
      btn.innerHTML = '<span class="material-symbols-outlined text-xl">check_circle</span><span class="text-base font-semibold">به سبد خرید افزوده شد!</span>';
      btn.classList.remove('brand-gradient-cta');
      btn.classList.add('bg-emerald-600');
      
      setTimeout(() => {
        btn.innerHTML = originalHTML;
        btn.classList.remove('bg-emerald-600');
        btn.classList.add('brand-gradient-cta');
      }, 2000);
    }
