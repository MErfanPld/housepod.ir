# core/forms.py
from django import forms


class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ("support", "پشتیبانی و سوالات"),
        ("order", "پیگیری سفارش"),
        ("product", "مشاوره محصول"),
        ("other", "سایر موارد"),
    ]

    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "نام الزامی است."},
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={"required": "شماره تماس الزامی است."},
    )
    email = forms.EmailField(required=False)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, required=True)
    message = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "پیام الزامی است."},
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        # ساده: فقط عدد و طول معقول
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("شماره تماس معتبر نیست.")
        return phone