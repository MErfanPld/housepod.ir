from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


def normalize_phone(value: str) -> str:
    value = str(value or "").strip().replace(" ", "").replace("-", "")
    persian = "۰۱۲۳۴۵۶۷۸۹"
    english = "0123456789"
    value = value.translate(str.maketrans(persian, english))
    arabic = "٠١٢٣٤٥٦٧٨٩"
    value = value.translate(str.maketrans(arabic, english))
    return value


class LoginForm(AuthenticationForm):
    """ورود با شماره موبایل + رمز عبور"""

    username = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 text-right py-3 pr-11 pl-4 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "۰۹۱۲۱۲۳۴۵۶۷",
                "dir": "ltr",
                "id": "login-phone",
                "autocomplete": "tel",
            }
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 py-3 pr-11 pl-11 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "رمز عبورت رو وارد کن",
                "id": "login-password",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean_username(self):
        return normalize_phone(self.cleaned_data.get("username", ""))


class RegisterForm(UserCreationForm):
    """ثبت‌نام با موبایل، نام و رمز"""

    first_name = forms.CharField(
        label="نام",
        max_length=80,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 py-2.5 pr-11 pl-4 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "نام",
            }
        ),
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=80,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 py-2.5 pr-11 pl-4 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "نام خانوادگی",
            }
        ),
    )
    phone = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 text-right py-2.5 pr-11 pl-4 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "۰۹۱۲۱۲۳۴۵۶۷",
                "dir": "ltr",
                "autocomplete": "tel",
            }
        ),
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 py-2.5 pr-11 pl-11 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "حداقل ۸ کاراکتر",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-xl bg-white border border-gray-200 py-2.5 pr-11 pl-11 focus:border-[#7628F5] focus:ring-2 focus:ring-[#7628F5]/20 outline-none",
                "placeholder": "رمز عبور را دوباره وارد کن",
                "autocomplete": "new-password",
            }
        ),
    )
    accept_terms = forms.BooleanField(
        label="پذیرش قوانین",
        required=True,
        error_messages={"required": "پذیرش قوانین و تأیید سن بالای ۱۸ الزامی است."},
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "password1", "password2")

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone", ""))
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class ProfileCompleteForm(forms.ModelForm):
    """تکمیل اطلاعات پروفایل و آدرس ارسال (برای سفارش)"""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "national_code",
            "province",
            "city",
            "postal_code",
            "address",
            "receiver_name",
            "receiver_phone",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"}),
            "last_name": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"}),
            "email": forms.EmailInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm", "dir": "ltr"}),
            "national_code": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm", "dir": "ltr", "maxlength": "10"}),
            "province": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"}),
            "city": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"}),
            "postal_code": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm", "dir": "ltr", "maxlength": "10"}),
            "address": forms.Textarea(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm", "rows": 3}),
            "receiver_name": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"}),
            "receiver_phone": forms.TextInput(attrs={"class": "w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm", "dir": "ltr"}),
        }

    def clean_receiver_phone(self):
        phone = self.cleaned_data.get("receiver_phone", "")
        if phone:
            return normalize_phone(phone)
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.check_profile_complete()
        return user
