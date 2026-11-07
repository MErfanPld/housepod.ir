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
