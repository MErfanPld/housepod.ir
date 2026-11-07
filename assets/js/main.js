/* ============================================
   VARIAN TECH - Unified Page Scripts
   Merged from account, blog_list, checkout,
   product_detail, payment_status (no name conflicts)
   ============================================ */


/* ---------- Account – auth tabs & password visibility ---------- */

function switchAuthTab(targetTab) {
      const loginTabBtn = document.getElementById('tab-btn-login');
      const registerTabBtn = document.getElementById('tab-btn-register');
      const loginFormContainer = document.getElementById('form-container-login');
      const registerFormContainer = document.getElementById('form-container-register');

      if (targetTab === 'login') {
        // Update Buttons
        loginTabBtn.className = "flex-1 py-2.5 px-4 rounded-xl font-label-md text-label-md font-semibold transition-all duration-200 flex items-center justify-center gap-2 bg-brand-purple text-white shadow-md glow-purple cursor-pointer";
        loginTabBtn.setAttribute('aria-selected', 'true');

        registerTabBtn.className = "flex-1 py-2.5 px-4 rounded-xl font-label-md text-label-md font-medium text-text-muted hover:text-text-primary transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer";
        registerTabBtn.setAttribute('aria-selected', 'false');

        // Animate Container
        registerFormContainer.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => {
          registerFormContainer.classList.add('hidden');
          registerFormContainer.classList.remove('block');

          loginFormContainer.classList.remove('hidden');
          loginFormContainer.classList.add('block');
          setTimeout(() => {
            loginFormContainer.classList.remove('opacity-0', 'translate-y-2');
          }, 20);
        }, 150);

      } else if (targetTab === 'register') {
        // Update Buttons
        registerTabBtn.className = "flex-1 py-2.5 px-4 rounded-xl font-label-md text-label-md font-semibold transition-all duration-200 flex items-center justify-center gap-2 bg-brand-purple text-white shadow-md glow-purple cursor-pointer";
        registerTabBtn.setAttribute('aria-selected', 'true');

        loginTabBtn.className = "flex-1 py-2.5 px-4 rounded-xl font-label-md text-label-md font-medium text-text-muted hover:text-text-primary transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer";
        loginTabBtn.setAttribute('aria-selected', 'false');

        // Animate Container
        loginFormContainer.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => {
          loginFormContainer.classList.add('hidden');
          loginFormContainer.classList.remove('block');

          registerFormContainer.classList.remove('hidden');
          registerFormContainer.classList.add('block');
          setTimeout(() => {
            registerFormContainer.classList.remove('opacity-0', 'translate-y-2');
          }, 20);
        }, 150);
      }
    }

    function togglePasswordVisibility(inputId, iconId) {
      const input = document.getElementById(inputId);
      const icon = document.getElementById(iconId);
      if (!input || !icon) return;

      if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = 'visibility_off';
      } else {
        input.type = 'password';
        icon.textContent = 'visibility';
      }
    }



/* ---------- Blog list – filters & search ---------- */

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



/* ---------- Product detail – qty, colors, tabs, gallery, cart ---------- */

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



/* ---------- Checkout – copy, modals, toast, upload ---------- */

// Copy text to clipboard with instant user feedback
    function copyToClipboard(text, btnElement) {
      if (!navigator.clipboard) {
        // Fallback
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand('copy');
          showToast('کپی شد: ' + text);
        } catch (err) {
          showToast('خطا در کپی متن');
        }
        document.body.removeChild(textArea);
        return;
      }

      navigator.clipboard.writeText(text).then(() => {
        showToast('با موفقیت کپی شد: ' + text);
        const originalContent = btnElement.innerHTML;
        btnElement.classList.add('bg-secondary', 'text-white');
        btnElement.innerHTML = `
          <span class="material-symbols-outlined text-[16px]">check</span>
          <span>کپی شد!</span>
        `;
        setTimeout(() => {
          btnElement.innerHTML = originalContent;
          btnElement.classList.remove('bg-secondary', 'text-white');
        }, 2200);
      }).catch(err => {
        showToast('خطا در کپی شماره');
      });
    }

    // Modal Control
    function showModal(id) {
      const modal = document.getElementById(id);
      const panel = document.getElementById(id + '-panel');
      if (!modal) return;
      modal.classList.remove('hidden');
      setTimeout(() => {
        modal.classList.remove('opacity-0');
        if (panel) {
          panel.classList.remove('scale-95');
          panel.classList.add('scale-100');
        }
      }, 20);
    }

    function hideModal(id) {
      const modal = document.getElementById(id);
      const panel = document.getElementById(id + '-panel');
      if (!modal) return;
      modal.classList.add('opacity-0');
      if (panel) {
        panel.classList.remove('scale-100');
        panel.classList.add('scale-95');
      }
      setTimeout(() => {
        modal.classList.add('hidden');
      }, 300);
    }

    // Toast Notifications
    function showToast(message, isError = false) {
      const toast = document.getElementById('toast');
      const toastMessage = document.getElementById('toast-message');
      const toastIcon = document.getElementById('toast-icon');
      
      toastMessage.innerText = message;
      if (isError) {
        toastIcon.innerText = 'error';
        toastIcon.className = 'material-symbols-outlined text-red-400 text-[20px]';
      } else {
        toastIcon.innerText = 'check_circle';
        toastIcon.className = 'material-symbols-outlined text-varian-lime text-[20px]';
      }

      toast.classList.remove('translate-y-24', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');

      setTimeout(() => {
        toast.classList.add('translate-y-24', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
      }, 3500);
    }

    // File Upload Simulation
    function removeUploadedFile() {
      const previewBox = document.getElementById('receipt-preview-box');
      if (previewBox) {
        previewBox.classList.add('opacity-50', 'pointer-events-none');
        setTimeout(() => {
          previewBox.remove();
          showToast('فایل رسید حذف شد. لطفاً فایل جدید را بارگذاری نمایید.', true);
        }, 200);
      }
    }

    // Main checkout trigger
    function triggerOrderSuccess() {
      const terms = document.getElementById('terms-checkbox');
      if (terms && !terms.checked) {
        showToast('لطفاً شرایط و قوانین خرید را تایید نمایید.', true);
        return;
      }
      showModal('success-modal');
    }

    // File input drag and drop highlight
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('receipt-file-input');

    if (dropzone && fileInput) {
      ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          dropzone.classList.add('border-varian-purple', 'bg-purple-50/50');
        }, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          dropzone.classList.remove('border-varian-purple', 'bg-purple-50/50');
        }, false);
      });

      fileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
          showToast('تصویر رسید (' + this.files[0].name + ') با موفقیت افزوده شد.');
        }
      });
    }



/* ---------- Payment status – order states & receipt ---------- */

function copyOrderCode() {
      const code = document.getElementById('order-code').innerText;
      navigator.clipboard.writeText(code).then(() => {
        alert('شماره سفارش ' + code + ' در کلیپ‌بورد کپی شد.');
      });
    }

    function toggleReceiptModal(show) {
      const modal = document.getElementById('receipt-modal');
      if (show) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      } else {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }

    // Interactive State Switcher for UI Verification & Showcase
    function setOrderStatus(state) {
      // Clear active states on simulator bar
      const tabs = ['pending', 'approved', 'rejected', 'processing'];
      tabs.forEach(t => {
        const btn = document.getElementById('tab-' + t);
        if (t === state) {
          btn.className = "px-3 py-1 rounded-full text-xs font-semibold bg-accent-lime text-primary transition-all";
        } else {
          btn.className = "px-3 py-1 rounded-full text-xs font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all";
        }
      });

      const heroCard = document.getElementById('hero-status-card');
      const heroIconContainer = document.getElementById('hero-icon-container');
      const heroIcon = document.getElementById('hero-icon');
      const pulseRing = document.getElementById('icon-pulse-ring');
      const heroHeading = document.getElementById('hero-heading');
      const statusBadge = document.getElementById('status-badge');
      const heroDesc = document.getElementById('hero-description');
      const reassuranceText = document.getElementById('reassurance-text');
      const ambientGlow = document.getElementById('hero-ambient-glow');
      const orderMetaStatus = document.getElementById('order-meta-status');
      const receiptBadge = document.getElementById('receipt-badge');

      // Timeline nodes
      const timelineStep3 = document.getElementById('timeline-step-3');
      const timelineStep3Icon = document.getElementById('timeline-step-3-icon');
      const timelineStep3Title = document.getElementById('timeline-step-3-title');
      const timelineStep3Status = document.getElementById('timeline-step-3-status');
      const timelineStep3Desc = document.getElementById('timeline-step-3-desc');
      const timelineStep4 = document.getElementById('timeline-step-4');
      const timelineStep4Icon = document.getElementById('timeline-step-4-icon');

      if (state === 'pending') {
        // State 1: Pending (Default)
        ambientGlow.className = "absolute -top-24 -left-24 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl pointer-events-none transition-all duration-500";
        heroIconContainer.className = "relative w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center";
        heroIcon.innerText = "hourglass_empty";
        pulseRing.className = "absolute -inset-2 rounded-full bg-amber-500/20 animate-pulse-ring";
        pulseRing.style.display = "block";
        heroHeading.innerText = "سفارش شما با موفقیت ثبت شد";
        statusBadge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300";
        statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span><span>در انتظار تأیید فیش پرداخت</span>';
        heroDesc.innerText = "اطلاعات سفارش و رسید پرداخت شما دریافت شد. پس از بررسی و تأیید پرداخت توسط تیم مالی و فروش، سفارش وارد مرحله آماده‌سازی و ارسال خواهد شد.";
        reassuranceText.innerText = "رسید شما در صف بررسی کارشناسان مالی واریان قرار دارد (بررسی در ساعات اداری ظرف حداکثر ۳۰ الی ۴۵ دقیقه انجام می‌شود).";
        orderMetaStatus.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-500"></span> در انتظار بررسی و انطباق بانکی';
        orderMetaStatus.className = "font-bold text-amber-700 text-sm flex items-center gap-1";
        receiptBadge.innerText = "دریافت شد؛ در انتظار تطبیق";
        receiptBadge.className = "px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200";

        // Timeline
        timelineStep3Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs ring-4 ring-amber-100";
        timelineStep3Icon.innerHTML = '<span class="material-symbols-outlined text-[13px]">hourglass_top</span>';
        timelineStep3Title.innerText = "بررسی و تأیید پرداخت";
        timelineStep3Title.className = "text-xs font-bold text-amber-700";
        timelineStep3Status.innerText = "مرحله جاری";
        timelineStep3Status.className = "text-[10px] font-semibold text-amber-600 bg-amber-50 px-2 py-0.5 rounded";
        timelineStep3Desc.innerText = "در حال استعلام حساب بانکی مقصد.";
        timelineStep4.classList.add('opacity-60');
      } 
      else if (state === 'approved') {
        // State 2: Approved
        ambientGlow.className = "absolute -top-24 -left-24 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none transition-all duration-500";
        heroIconContainer.className = "relative w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center";
        heroIcon.innerText = "check_circle";
        pulseRing.className = "absolute -inset-2 rounded-full bg-emerald-500/20";
        pulseRing.style.display = "block";
        heroHeading.innerText = "پرداخت شما با موفقیت تأیید شد";
        statusBadge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300";
        statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-600"></span><span>تأیید شده و پرداخت موفق</span>';
        heroDesc.innerText = "رسید واریزی با حساب بانکی تطبیق داده شد و فاکتور نهایی صادر گردید. کالاها به واحد انبارداری تحویل داده شدند.";
        reassuranceText.innerText = "فاکتور الکترونیک پرداخت صادر گردید و فیش شما مهر تایید مالی خورد.";
        orderMetaStatus.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span> پرداخت شده و معتبر';
        orderMetaStatus.className = "font-bold text-emerald-700 text-sm flex items-center gap-1";
        receiptBadge.innerText = "تأیید شده توسط حسابداری";
        receiptBadge.className = "px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200";

        // Timeline
        timelineStep3Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-primary text-accent-lime flex items-center justify-center text-xs";
        timelineStep3Icon.innerHTML = '<span class="material-symbols-outlined text-[14px]">check</span>';
        timelineStep3Title.innerText = "تأیید قطعی فیش";
        timelineStep3Title.className = "text-xs font-bold text-text-primary";
        timelineStep3Status.innerText = "تکمیل شده";
        timelineStep3Status.className = "text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded";
        timelineStep3Desc.innerText = "مبلغ واریزی ۵,۲۳۰,۰۰۰ تومان احراز گردید.";

        timelineStep4.classList.remove('opacity-60');
        timelineStep4Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-primary text-accent-lime flex items-center justify-center text-xs ring-4 ring-neutral-200";
      } 
      else if (state === 'rejected') {
        // State 3: Rejected / Invalid
        ambientGlow.className = "absolute -top-24 -left-24 w-80 h-80 rounded-full bg-red-500/10 blur-3xl pointer-events-none transition-all duration-500";
        heroIconContainer.className = "relative w-16 h-16 rounded-2xl bg-red-50 border border-red-200 text-red-600 flex items-center justify-center";
        heroIcon.innerText = "error";
        pulseRing.className = "absolute -inset-2 rounded-full bg-red-500/20";
        pulseRing.style.display = "block";
        heroHeading.innerText = "فیش واریزی نیاز به بررسی مجدد دارد";
        statusBadge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-300";
        statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-600"></span><span>فیش نامعتبر / ناخوانا</span>';
        heroDesc.innerText = "علت: تصویر فیش ارسالی ناخوانا بوده یا مبلغ واریز شده کمتر از صورت‌حساب است. لطفاً فیش صحیح را مجدداً بارگذاری فرمایید.";
        reassuranceText.innerText = "کارشناسان پشتیبانی واریان آماده راهنمایی شما هستند: لطفاً از طریق دکمه بارگذاری، رسید جدید را ارسال کنید.";
        orderMetaStatus.innerHTML = '<span class="w-2 h-2 rounded-full bg-red-500"></span> رد فیش توسط دپارتمان مالی';
        orderMetaStatus.className = "font-bold text-red-700 text-sm flex items-center gap-1";
        receiptBadge.innerText = "رد شده (نیاز به ارسال مجدد)";
        receiptBadge.className = "px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200";

        // Timeline
        timelineStep3Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-red-600 text-white flex items-center justify-center text-xs ring-4 ring-red-100";
        timelineStep3Icon.innerHTML = '<span class="material-symbols-outlined text-[13px]">close</span>';
        timelineStep3Title.innerText = "مغایرت در فیش واریزی";
        timelineStep3Title.className = "text-xs font-bold text-red-700";
        timelineStep3Status.innerText = "متوقف شده";
        timelineStep3Status.className = "text-[10px] font-semibold text-red-600 bg-red-50 px-2 py-0.5 rounded";
        timelineStep3Desc.innerText = "نیازمند بارگذاری مجدد رسید.";
        timelineStep4.classList.add('opacity-60');
      }
      else if (state === 'processing') {
        // State 4: Packaging & Processing
        ambientGlow.className = "absolute -top-24 -left-24 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none transition-all duration-500";
        heroIconContainer.className = "relative w-16 h-16 rounded-2xl bg-cyan-50 border border-cyan-200 text-cyan-700 flex items-center justify-center";
        heroIcon.innerText = "inventory_2";
        pulseRing.className = "absolute -inset-2 rounded-full bg-cyan-500/20";
        heroHeading.innerText = "سفارش در حال پردازش و آماده‌سازی";
        statusBadge.className = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-100 text-cyan-900 border border-cyan-300";
        statusBadge.innerHTML = '<span class="w-2 h-2 rounded-full bg-cyan-600 animate-pulse"></span><span>آماده‌سازی در انبار مرکزی</span>';
        heroDesc.innerText = "اقلام پاد سیستم و آیکاس جهت تست اولیه سلامت جعبه پلمپ وکیوم شده و بارنامه پستی صادر شده است.";
        reassuranceText.innerText = "بسته ظرف ۴ ساعت آینده تحویل مامور پست پیشتاز خواهد شد.";
        orderMetaStatus.innerHTML = '<span class="w-2 h-2 rounded-full bg-cyan-600"></span> در حال بسته‌بندی ایمن';
        orderMetaStatus.className = "font-bold text-cyan-800 text-sm flex items-center gap-1";
        receiptBadge.innerText = "تأیید و بایگانی شد";
        receiptBadge.className = "px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-100 text-cyan-800 border border-cyan-200";

        // Timeline
        timelineStep3Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-primary text-accent-lime flex items-center justify-center text-xs";
        timelineStep3Icon.innerHTML = '<span class="material-symbols-outlined text-[14px]">check</span>';
        timelineStep4.classList.remove('opacity-60');
        timelineStep4Icon.className = "absolute -right-6 top-1 w-5 h-5 rounded-full bg-cyan-600 text-white flex items-center justify-center text-xs ring-4 ring-cyan-100";
        timelineStep4Icon.innerHTML = '<span class="material-symbols-outlined text-[13px]">inventory_2</span>';
      }
    }

