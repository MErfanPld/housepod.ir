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
