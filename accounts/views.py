from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import LoginForm, RegisterForm, ProfileCompleteForm
from .models import User


class UserLoginView(LoginView):
    template_name = "accounts/auth.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        return next_url or reverse_lazy("accounts:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_form"] = context.get("form") or LoginForm()
        context["register_form"] = RegisterForm()
        context["active_tab"] = "login"
        return context

    def form_invalid(self, form):
        messages.error(self.request, "شماره موبایل یا رمز عبور اشتباه است.")
        return super().form_invalid(form)


class UserRegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/auth.html"
    success_url = reverse_lazy("accounts:profile_complete")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            "حساب کاربری ساخته شد. لطفاً اطلاعات ارسال را تکمیل کنید.",
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["register_form"] = context.get("form") or RegisterForm()
        context["login_form"] = LoginForm()
        context["active_tab"] = "register"
        return context


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("products:product_list")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["profile_user"] = user
        context["addresses"] = user.addresses.all()
        context["needs_complete"] = not user.check_profile_complete()
        return context


class ProfileCompleteView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileCompleteForm
    template_name = "accounts/profile_complete.html"
    success_url = reverse_lazy("accounts:profile")
    login_url = reverse_lazy("accounts:login")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات پروفایل با موفقیت ذخیره شد.")
        return super().form_valid(form)