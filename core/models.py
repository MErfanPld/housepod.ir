from django.db import models
from django.core.validators import FileExtensionValidator

class HeroSlide(models.Model):
    # متن‌ها
    badge_text = models.CharField("متن بج", max_length=80, blank=True, help_text="مثال: دنیای دستگاه‌های نسل جدید ۲۰۲۴")
    title_line1 = models.CharField("عنوان خط اول", max_length=120)
    title_highlight = models.CharField("قسمت هایلایت عنوان", max_length=80, blank=True, help_text="بخش رنگی عنوان")
    description = models.TextField("توضیحات", blank=True)

    # دکمه اصلی
    primary_btn_text = models.CharField("متن دکمه اصلی", max_length=50, default="مشاهده محصولات")
    primary_btn_url = models.CharField("لینک دکمه اصلی", max_length=255, default="#catalog")

    # دکمه ثانویه
    secondary_btn_text = models.CharField("متن دکمه ثانویه", max_length=50, blank=True, default="کشف دسته‌بندی‌ها")
    secondary_btn_url = models.CharField("لینک دکمه ثانویه", max_length=255, blank=True, default="#categories")

    # تصویر
    image = models.ImageField(
        "تصویر اسلاید",
        upload_to="hero/",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="نسبت پیشنهادی ۴:۵ یا نزدیک به آن"
    )
    image_alt = models.CharField("متن جایگزین تصویر", max_length=255, blank=True)

    # بج‌های شناور روی تصویر
    top_left_badge = models.CharField("بج بالا چپ", max_length=60, blank=True, default="کالکشن ویژه ۲۰۲۴")
    top_right_badge = models.CharField("بج بالا راست", max_length=60, blank=True, default="IQOS & OXVA PRO")

    # کارت مشخصات پایین تصویر
    feature_title = models.CharField("عنوان ویژگی", max_length=80, blank=True, default="تکنولوژی گرمایش هوشمند")
    feature_subtitle = models.CharField("زیرعنوان ویژگی", max_length=80, blank=True, default="IQOS ILUMA & POD X")
    price_label = models.CharField("برچسب قیمت", max_length=30, blank=True, default="شروع از")
    price = models.CharField("قیمت", max_length=40, blank=True, help_text="مثال: ۱,۸۹۰,۰۰۰")

    # اعتماد (Trust badges) - اختیاری
    trust_badge_1 = models.CharField("بج اعتماد ۱", max_length=80, blank=True, default="ضمانت ۷ روزه سلامت فیزیکی")
    trust_badge_2 = models.CharField("بج اعتماد ۲", max_length=80, blank=True, default="ارسال اکسپرس در همان روز")
    trust_badge_3 = models.CharField("بج اعتماد ۳", max_length=80, blank=True, default="بیش از ۲۰۰ مدل اورجینال")

    # کنترل
    is_active = models.BooleanField("فعال", default=True)
    order = models.PositiveIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "اسلاید هیرو"
        verbose_name_plural = "اسلایدهای هیرو"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.title_line1} {self.title_highlight}".strip()



from django.db import models
from django.core.validators import MinValueValidator


class HomeBanner(models.Model):
    """بنرهای تبلیغاتی صفحه اصلی."""

    class Placement(models.TextChoices):
        PROMO_LEFT = "promo_left", "بنر تبلیغاتی اول"
        PROMO_RIGHT = "promo_right", "بنر تبلیغاتی دوم"
        WIDE = "wide", "بنر عریض"
        BOTTOM = "bottom", "بنر انتهایی"

    title = models.CharField(
        max_length=180,
        verbose_name="عنوان داخلی بنر",
    )
    eyebrow = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="متن بالای عنوان",
    )
    heading = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان نمایشی",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    image = models.ImageField(
        upload_to="home/banners/",
        verbose_name="تصویر بنر",
    )
    mobile_image = models.ImageField(
        upload_to="home/banners/mobile/",
        blank=True,
        null=True,
        verbose_name="تصویر موبایل",
    )
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="متن جایگزین تصویر",
    )
    button_text = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="متن دکمه",
    )
    button_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="آدرس مقصد",
    )
    placement = models.CharField(
        max_length=20,
        choices=Placement.choices,
        default=Placement.WIDE,
        db_index=True,
        verbose_name="محل نمایش",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="شروع نمایش",
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="پایان نمایش",
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
        verbose_name = "بنر صفحه خانه"
        verbose_name_plural = "بنرهای صفحه خانه"
        ordering = ("placement", "order", "id")

    def __str__(self):
        return self.title


class StoreFeature(models.Model):
    """مزیت‌ها و خدمات فروشگاه."""

    title = models.CharField(
        max_length=120,
        verbose_name="عنوان",
    )
    description = models.CharField(
        max_length=250,
        verbose_name="توضیحات",
    )
    icon = models.CharField(
        max_length=80,
        default="verified",
        verbose_name="نام آیکون",
        help_text="نام آیکون Material Symbols، مانند local_shipping",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "مزیت فروشگاه"
        verbose_name_plural = "مزیت‌های فروشگاه"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class HomeStatistic(models.Model):
    """آمار نمایشی صفحه اصلی."""

    title = models.CharField(
        max_length=120,
        verbose_name="عنوان آمار",
    )
    value = models.CharField(
        max_length=50,
        verbose_name="مقدار",
        help_text="مثلاً ۱۲۰۰+ یا ۲۴",
    )
    suffix = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="پسوند",
        help_text="مثلاً محصول یا مشتری",
    )
    icon = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="نام آیکون",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "آمار صفحه خانه"
        verbose_name_plural = "آمار صفحه خانه"
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.title}: {self.value}"


class HomeFAQ(models.Model):
    """پرسش‌های متداول صفحه اصلی."""

    question = models.CharField(
        max_length=300,
        verbose_name="سؤال",
    )
    answer = models.TextField(
        verbose_name="پاسخ",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "پرسش متداول صفحه خانه"
        verbose_name_plural = "پرسش‌های متداول صفحه خانه"
        ordering = ("order", "id")

    def __str__(self):
        return self.question
    