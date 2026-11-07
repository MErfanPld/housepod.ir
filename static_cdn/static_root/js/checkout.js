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
