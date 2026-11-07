from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse


phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد (مثال: ۰۹۱۲۱۲۳۴۵۶۷).",
)


class UserManager(BaseUserManager):
    """مدیریت ساخت کاربر با شماره موبایل به‌جای username"""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("شماره موبایل الزامی است.")
        phone = str(phone).strip().replace(" ", "")
        # تبدیل اعداد فارسی به انگلیسی در صورت نیاز
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"
        trans = str.maketrans(persian_digits, english_digits)
        phone = phone.translate(trans)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("سوپریوزر باید is_staff=True باشد.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("سوپریوزر باید is_superuser=True باشد.")
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name="شماره موبایل",
        help_text="مثال: ۰۹۱۲۱۲۳۴۵۶۷ — با این شماره وارد می‌شوید",
    )
    first_name = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="نام",
    )
    last_name = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="نام خانوادگی",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل",
        help_text="اختیاری — برای فاکتور و اطلاع‌رسانی",
    )
    national_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="کد ملی",
        help_text="اختیاری — برای فاکتور رسمی",
    )

    # آدرس پیش‌فرض ارسال (برای checkout سریع)
    province = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="استان",
    )
    city = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="شهر",
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="کد پستی",
    )
    address = models.TextField(
        blank=True,
        verbose_name="آدرس کامل",
        help_text="خیابان، کوچه، پلاک، واحد",
    )
    receiver_name = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="نام گیرنده",
        help_text="اگر خالی باشد از نام خود کاربر استفاده می‌شود",
    )
    receiver_phone = models.CharField(
        max_length=11,
        blank=True,
        verbose_name="موبایل گیرنده",
        help_text="اگر خالی باشد از موبایل حساب استفاده می‌شود",
    )

    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name="موبایل تأیید شده",
    )
    is_profile_complete = models.BooleanField(
        default=False,
        verbose_name="پروفایل تکمیل شده",
        help_text="برای ثبت سفارش، نام و آدرس ارسال لازم است",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="دسترسی ادمین",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ عضویت",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # برای createsuperuser فقط phone + password

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        name = self.get_full_name()
        return f"{name} ({self.phone})" if name else self.phone

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name or self.phone

    def check_profile_complete(self) -> bool:
        """آیا اطلاعات لازم برای ارسال سفارش کامل است؟"""
        complete = bool(
            self.first_name
            and self.last_name
            and self.province
            and self.city
            and self.address
            and self.postal_code
        )
        if self.is_profile_complete != complete:
            type(self).objects.filter(pk=self.pk).update(is_profile_complete=complete)
            self.is_profile_complete = complete
        return complete

    def get_shipping_receiver(self) -> str:
        return self.receiver_name or self.get_full_name()

    def get_shipping_phone(self) -> str:
        return self.receiver_phone or self.phone

    def get_absolute_url(self):
        return reverse("accounts:profile")


class Address(models.Model):
    """آدرس‌های اضافی کاربر (چند آدرس ارسال)"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="کاربر",
    )
    title = models.CharField(
        max_length=50,
        verbose_name="عنوان آدرس",
        help_text="مثلاً: خانه، محل کار",
    )
    receiver_name = models.CharField(
        max_length=120,
        verbose_name="نام گیرنده",
    )
    receiver_phone = models.CharField(
        max_length=11,
        validators=[phone_validator],
        verbose_name="موبایل گیرنده",
    )
    province = models.CharField(
        max_length=80,
        verbose_name="استان",
    )
    city = models.CharField(
        max_length=80,
        verbose_name="شهر",
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name="کد پستی",
    )
    address = models.TextField(
        verbose_name="آدرس کامل",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="آدرس پیش‌فرض",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)
