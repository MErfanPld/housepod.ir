from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    """دسته‌بندی محصولات (پاد، دستگاه IQOS، لوازم جانبی و ...)"""

    GRADIENT_CHOICES = [
        ("purple", "بنفش الکتریک"),
        ("charcoal", "ذغالی + نارنجی"),
        ("magenta", "سرخابی"),
        ("cyan", "فیروزه‌ای"),
        ("lime", "سبز لیمویی"),
        ("orange", "نارنجی غروب"),
    ]

    name = models.CharField(max_length=150, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    english_name = models.CharField(max_length=100, blank=True, verbose_name="نام انگلیسی", help_text="مثال: Pod Systems")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="تصویر دسته‌بندی")
    
    # ظاهر کارت
    badge_text = models.CharField(max_length=60, blank=True, verbose_name="متن بج", help_text="مثال: ۴۸ مدل فعال")
    gradient = models.CharField(max_length=20, choices=GRADIENT_CHOICES, default="purple", verbose_name="گرادینت کارت")
    link_text = models.CharField(max_length=50, default="مشاهده مدل‌ها", verbose_name="متن لینک")
    
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="دسته‌بندی والد"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_list_by_category", kwargs={"slug": self.slug})


class Product(models.Model):
    """محصولات فروشگاه (پاد IQOS، دستگاه، لوازم جانبی و ...)"""

    class DeviceCompatibility(models.TextChoices):
        ILUMA = "iluma", "IQOS ILUMA"
        ILUMA_PRIME = "iluma_prime", "IQOS ILUMA PRIME"
        ILUMA_ONE = "iluma_one", "IQOS ILUMA ONE"
        ORIGINAL = "original", "IQOS Original / 3"
        MULTI = "multi", "چند دستگاهی / عمومی"
        OTHER = "other", "سایر"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="نام محصول",
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام انگلیسی / زیرعنوان",
        help_text="مثلاً: OXVA Xlim Pro 2 Pod Kit • 30W Maximum Output",
    )
    slug = models.SlugField(
        max_length=270,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
        help_text="برای استفاده در URL (به صورت خودکار از نام ساخته می‌شود)",
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد کالا (SKU)",
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="برند",
        help_text="مثلاً: OXVA، IQOS، Vaporesso",
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیح کوتاه",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات کامل / بررسی تخصصی",
    )
    specs = models.TextField(
        blank=True,
        verbose_name="مشخصات فنی",
        help_text="هر خط یک مشخصه: برچسب|مقدار  مثلاً: ظرفیت باتری|۱۰۰۰ میلی‌آمپر",
    )
    usage_guide = models.TextField(
        blank=True,
        verbose_name="راهنمای استفاده و نگهداری",
    )
    badge_1 = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="بج مشخصات ۱",
        help_text="مثلاً: توان ۳۰ وات واقعی",
    )
    badge_2 = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="بج مشخصات ۲",
        help_text="مثلاً: باتری ۱۰۰۰ میلی‌آمپر",
    )
    badge_3 = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="بج مشخصات ۳",
        help_text="مثلاً: شارژ فوق سریع Type-C",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت (تومان)",
    )
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت با تخفیف (تومان)",
        help_text="در صورت خالی بودن، قیمت اصلی نمایش داده می‌شود",
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی انبار",
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="تصویر اصلی",
    )
    flavor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="طعم / طعم‌دهی",
        help_text="مثلاً: منتول، توت‌فرنگی، تنباکو کلاسیک",
    )
    compatibility = models.CharField(
        max_length=20,
        choices=DeviceCompatibility.choices,
        default=DeviceCompatibility.MULTI,
        verbose_name="سازگاری با دستگاه",
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="امتیاز میانگین",
        help_text="از ۰ تا ۵",
    )
    reviews_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد نظرات",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال / قابل نمایش",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="محصول ویژه",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود برای فروش",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_available"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            self.slug = base_slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def final_price(self):
        """قیمت نهایی قابل پرداخت"""
        if self.price is None:
            return None
        if (
            self.discount_price is not None
            and self.discount_price < self.price
        ):
            return self.discount_price
        return self.price

    @property
    def has_discount(self) -> bool:
        if self.price is None or self.discount_price is None:
            return False
        return self.discount_price < self.price

    @property
    def discount_percent(self) -> int:
        if not self.has_discount or not self.price:
            return 0
        return int(((self.price - self.discount_price) / self.price) * 100)

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0 and self.is_available and self.is_active

    def get_specs_list(self):
        """لیست مشخصات فنی از فیلد specs (فرمت: برچسب|مقدار در هر خط)"""
        if not self.specs:
            return []
        rows = []
        for line in self.specs.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                label, value = line.split("|", 1)
                rows.append({"label": label.strip(), "value": value.strip()})
            else:
                rows.append({"label": "", "value": line})
        return rows


class ProductImage(models.Model):
    """تصاویر گالری محصول"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول",
    )
    image = models.ImageField(
        upload_to="products/gallery/",
        verbose_name="تصویر",
    )
    alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="متن جایگزین",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} - تصویر {self.order or self.pk}"
