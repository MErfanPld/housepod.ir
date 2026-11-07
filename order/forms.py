import os

from django import forms
from PIL import Image, UnidentifiedImageError

from .models import PaymentReceipt

INPUT_CLASS = "w-full rounded-xl border px-4 py-2.5 text-sm"

RECEIPT_MAX_SIZE = 5 * 1024 * 1024  # ۵ مگابایت
RECEIPT_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
RECEIPT_PDF_EXTENSION = ".pdf"


class CheckoutForm(forms.Form):
    receiver_name = forms.CharField(
        label="نام گیرنده",
        max_length=120,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    receiver_phone = forms.CharField(
        label="موبایل گیرنده",
        max_length=11,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "dir": "ltr"}),
    )
    province = forms.CharField(
        label="استان",
        max_length=80,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    city = forms.CharField(
        label="شهر",
        max_length=80,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    postal_code = forms.CharField(
        label="کد پستی",
        max_length=10,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "dir": "ltr"}),
    )
    address = forms.CharField(
        label="آدرس کامل",
        widget=forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
    )
    user_note = forms.CharField(
        label="توضیحات سفارش (اختیاری)",
        required=False,
        widget=forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
    )


class ReceiptUploadForm(forms.ModelForm):
    # فیلد مدل ImageField است؛ فیلد فرم ImageField هر فایلی را که Pillow باز نکند
    # (مثل PDF) رد می‌کند. FileField + اعتبارسنجی دستی، هم تصویر و هم PDF را قبول می‌کند.
    image = forms.FileField(
        label="تصویر یا PDF فیش واریز",
        help_text="فرمت‌های مجاز: JPG، PNG، WEBP یا PDF — حداکثر ۵ مگابایت",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full text-sm",
                "accept": "image/jpeg,image/png,image/webp,application/pdf,.jpg,.jpeg,.png,.webp,.pdf",
            }
        ),
        error_messages={"required": "لطفاً تصویر یا فایل فیش را انتخاب کنید."},
    )

    class Meta:
        model = PaymentReceipt
        fields = ("image", "tracking_code", "amount")
        widgets = {
            "tracking_code": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "کد پیگیری در صورت وجود",
                    "dir": "ltr",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مبلغ واریزی (تومان)",
                    "dir": "ltr",
                    "min": "0",
                }
            ),
        }
        labels = {
            "tracking_code": "کد پیگیری",
            "amount": "مبلغ واریزی",
        }

    def clean_image(self):
        uploaded = self.cleaned_data.get("image")
        if not uploaded:
            return uploaded

        if uploaded.size > RECEIPT_MAX_SIZE:
            raise forms.ValidationError("حجم فایل بیشتر از ۵ مگابایت است.")

        ext = os.path.splitext(uploaded.name)[1].lower()

        if ext == RECEIPT_PDF_EXTENSION:
            header = uploaded.read(5)
            uploaded.seek(0)
            if not header.startswith(b"%PDF"):
                raise forms.ValidationError("فایل PDF معتبر نیست یا آسیب دیده است.")
            return uploaded

        if ext not in RECEIPT_IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                "فرمت فایل پشتیبانی نمی‌شود. لطفاً JPG، PNG، WEBP یا PDF ارسال کنید."
            )

        try:
            with Image.open(uploaded) as img:
                img.verify()
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            raise forms.ValidationError(
                "تصویر قابل خواندن نیست. اگر با آیفون عکس گرفته‌اید (HEIC)، "
                "از رسید اسکرین‌شات بگیرید و همان را ارسال کنید."
            )
        finally:
            uploaded.seek(0)
        return uploaded

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("مبلغ باید بیشتر از صفر باشد.")
        return amount