from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class BankAccount(models.Model):
    """شماره کارت / حساب برای پرداخت کارت‌به‌کارت (قابل مدیریت از ادمین)"""

    title = models.CharField(
        max_length=100,
        verbose_name="عنوان",
        help_text="مثلاً: کارت اصلی فروشگاه",
    )
    owner_name = models.CharField(
        max_length=120,
        verbose_name="نام صاحب حساب",
    )
    card_number = models.CharField(
        max_length=19,
        verbose_name="شماره کارت",
        help_text="۱۶ رقم — با یا بدون خط تیره",
    )
    bank_name = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="نام بانک",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        verbose_name = "حساب بانکی / کارت"
        verbose_name_plural = "حساب‌های کارت‌به‌کارت"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.owner_name} — {self.card_number}"

    def formatted_card(self) -> str:
        digits = "".join(c for c in self.card_number if c.isdigit())
        if len(digits) == 16:
            return " ".join(digits[i : i + 4] for i in range(0, 16, 4))
        return self.card_number


class Cart(models.Model):
    """سبد خرید — برای کاربر لاگین یا با session_key برای مهمان"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
        verbose_name="کاربر",
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="کلید نشست",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self) -> str:
        if self.user_id:
            return f"سبد {self.user}"
        return f"سبد نشست {self.session_key[:8]}…"

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self) -> Decimal:
        return sum(
            (item.line_total for item in self.items.select_related("product")),
            Decimal("0"),
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="محصول",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="تعداد",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سبد"
        verbose_name_plural = "آیتم‌های سبد"
        unique_together = [("cart", "product")]

    def __str__(self) -> str:
        return f"{self.product} × {self.quantity}"

    @property
    def unit_price(self) -> Decimal:
        price = self.product.final_price
        return price if price is not None else Decimal("0")

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class Order(models.Model):
    """سفارش ثبت‌شده"""

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "در انتظار پرداخت"
        AWAITING_VERIFY = "awaiting_verify", "در انتظار تأیید فیش"
        CONFIRMED = "confirmed", "تأیید شده"
        PROCESSING = "processing", "در حال آماده‌سازی"
        SHIPPED = "shipped", "ارسال شده"
        DELIVERED = "delivered", "تحویل شده"
        REJECTED = "rejected", "رد فیش / ناموفق"
        CANCELLED = "cancelled", "لغو شده"

    class PaymentMethod(models.TextChoices):
        CARD_TO_CARD = "card_to_card", "کارت به کارت"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="شماره سفارش",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
        verbose_name="وضعیت",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD_TO_CARD,
        verbose_name="روش پرداخت",
    )

    # آدرس ارسال (کپی از پروفایل در لحظه سفارش)
    receiver_name = models.CharField(max_length=120, verbose_name="نام گیرنده")
    receiver_phone = models.CharField(max_length=11, verbose_name="موبایل گیرنده")
    province = models.CharField(max_length=80, verbose_name="استان")
    city = models.CharField(max_length=80, verbose_name="شهر")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    address = models.TextField(verbose_name="آدرس کامل")

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name="جمع کالاها (تومان)",
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="هزینه ارسال (تومان)",
    )
    total = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name="مبلغ کل (تومان)",
    )
    user_note = models.TextField(
        blank=True,
        verbose_name="توضیح مشتری",
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name="یادداشت ادمین",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کارت مقصد",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی")
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تأیید پرداخت",
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"سفارش {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number() -> str:
        # مثلاً: 14031104-A3F2
        now = timezone.localtime()
        prefix = now.strftime("%y%m%d%H%M")
        import secrets

        suffix = secrets.token_hex(2).upper()
        return f"{prefix}{suffix}"

    def get_absolute_url(self):
        return reverse("order:order_detail", kwargs={"order_number": self.order_number})

    @property
    def can_upload_receipt(self) -> bool:
        return self.status in {
            self.Status.PENDING_PAYMENT,
            self.Status.AWAITING_VERIFY,
            self.Status.REJECTED,
        }

    def mark_awaiting_verify(self):
        self.status = self.Status.AWAITING_VERIFY
        self.save(update_fields=["status", "updated_at"])

    def mark_confirmed(self):
        self.status = self.Status.CONFIRMED
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])

    def mark_rejected(self):
        self.status = self.Status.REJECTED
        self.save(update_fields=["status", "updated_at"])


class OrderItem(models.Model):
    """آیتم سفارش — قیمت در لحظه خرید قفل می‌شود"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="محصول",
    )
    product_name = models.CharField(max_length=255, verbose_name="نام محصول")
    product_sku = models.CharField(max_length=50, blank=True, verbose_name="SKU")
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="قیمت واحد",
    )
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        verbose_name="جمع ردیف",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"


class PaymentReceipt(models.Model):
    """فیش واریز کارت‌به‌کارت — تا تأیید ادمین"""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name="سفارش",
    )
    image = models.ImageField(
        upload_to="receipts/%Y/%m/",
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "webp", "pdf"]),
        ],
        verbose_name="تصویر / فایل فیش",
    )
    tracking_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد پیگیری / ارجاع بانکی",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="مبلغ اعلامی مشتری",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="وضعیت بررسی",
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name="توضیح ادمین",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان آپلود")
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بررسی",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_receipts",
        verbose_name="بررسی‌کننده",
    )

    class Meta:
        verbose_name = "فیش پرداخت"
        verbose_name_plural = "فیش‌های پرداخت"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"فیش {self.order.order_number} — {self.get_status_display()}"
