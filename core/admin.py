from django import forms
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from core.templatetags.core_tags import fa_num, jalali

from .models import HeroSlide, HomeBanner, HomeFAQ, HomeStatistic, StoreFeature

# ---------------------------------------------------------------------- #
# عنوان‌های پنل مدیریت
# ---------------------------------------------------------------------- #
admin.site.site_header = "پنل مدیریت واریان"
admin.site.site_title = "مدیریت واریان"
admin.site.index_title = "مدیریت محتوای فروشگاه"

MATERIAL_ICONS_CSS = (
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:"
    "wght,FILL@100..700,0..1&display=swap"
)


# ---------------------------------------------------------------------- #
# ابزارهای مشترک
# ---------------------------------------------------------------------- #
def image_preview(file_field, height=60, rounded=8):
    if not file_field:
        return format_html('<span style="color:#999;">بدون تصویر</span>')
    return format_html(
        '<a href="{0}" target="_blank"><img src="{0}" style="max-height:{1}px;max-width:160px;'
        'border-radius:{2}px;border:1px solid #eee;object-fit:contain;background:#fafafa;"/></a>',
        file_field.url, height, rounded,
    )


def icon_preview(name):
    if not name:
        return "—"
    return format_html(
        '<span class="material-symbols-outlined" style="font-size:22px;vertical-align:middle;'
        'color:#6A1FE9;">{0}</span> <code style="font-size:11px;color:#888;">{0}</code>',
        name,
    )


def badge(text, color, bg):
    return format_html(
        '<span style="display:inline-block;padding:2px 10px;border-radius:999px;font-size:11px;'
        'font-weight:700;color:{};background:{};">{}</span>',
        color, bg, text,
    )


class ActivationActionsMixin:
    """اکشن‌های فعال / غیرفعال کردن گروهی"""

    actions = ("make_active", "make_inactive")

    @admin.action(description="فعال کردن موارد انتخاب‌شده")
    def make_active(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{fa_num(count)} مورد فعال شد.", messages.SUCCESS)

    @admin.action(description="غیرفعال کردن موارد انتخاب‌شده")
    def make_inactive(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{fa_num(count)} مورد غیرفعال شد.", messages.WARNING)


class BaseContentAdmin(ActivationActionsMixin, admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True
    list_editable = ("order", "is_active")


# ---------------------------------------------------------------------- #
# اسلایدر هیرو
# ---------------------------------------------------------------------- #
@admin.register(HeroSlide)
class HeroSlideAdmin(BaseContentAdmin):
    list_display = ("thumb", "full_title", "badge_text", "price_display", "order", "is_active", "updated_display")
    list_display_links = ("thumb", "full_title")
    list_filter = ("is_active",)
    search_fields = ("title_line1", "title_highlight", "description", "badge_text")
    readonly_fields = ("large_preview", "created_display", "updated_display")
    ordering = ("order", "-created_at")

    fieldsets = (
        ("متن اسلاید", {
            "fields": ("badge_text", ("title_line1", "title_highlight"), "description"),
        }),
        ("دکمه‌ها", {
            "fields": (("primary_btn_text", "primary_btn_url"), ("secondary_btn_text", "secondary_btn_url")),
            "description": "لینک می‌تواند آدرس کامل، مسیر داخلی (مثل /products/) یا لنگر صفحه (مثل #catalog) باشد.",
        }),
        ("تصویر", {
            "fields": ("image", "large_preview", "image_alt"),
        }),
        ("بج‌ها و کارت قیمت روی تصویر", {
            "fields": (("top_left_badge", "top_right_badge"), ("feature_title", "feature_subtitle"), ("price_label", "price")),
        }),
        ("بج‌های اعتماد", {
            "fields": ("trust_badge_1", "trust_badge_2", "trust_badge_3"),
            "classes": ("collapse",),
        }),
        ("تنظیمات نمایش", {
            "fields": (("is_active", "order"), ("created_display", "updated_display")),
        }),
    )

    @admin.display(description="تصویر")
    def thumb(self, obj):
        return image_preview(obj.image, 50)

    @admin.display(description="پیش‌نمایش")
    def large_preview(self, obj):
        return image_preview(obj.image if obj.pk else None, 220, 14)

    @admin.display(description="عنوان", ordering="title_line1")
    def full_title(self, obj):
        if obj.title_highlight:
            return format_html('{} <strong style="color:#6A1FE9;">{}</strong>', obj.title_line1, obj.title_highlight)
        return obj.title_line1

    @admin.display(description="قیمت")
    def price_display(self, obj):
        if not obj.price:
            return "—"
        return f"{obj.price_label} {fa_num(obj.price)} تومان".strip()

    @admin.display(description="تاریخ ایجاد")
    def created_display(self, obj):
        return jalali(obj.created_at) if obj.pk else "—"

    @admin.display(description="آخرین ویرایش", ordering="updated_at")
    def updated_display(self, obj):
        return jalali(obj.updated_at) if obj.pk else "—"


# ---------------------------------------------------------------------- #
# بنرها
# ---------------------------------------------------------------------- #
class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        starts, ends = cleaned.get("starts_at"), cleaned.get("ends_at")
        if starts and ends and ends <= starts:
            self.add_error("ends_at", "زمان پایان باید بعد از زمان شروع باشد.")
        return cleaned


@admin.register(HomeBanner)
class HomeBannerAdmin(BaseContentAdmin):
    form = HomeBannerForm
    list_display = ("thumb", "title", "placement", "schedule_status", "order", "is_active")
    list_display_links = ("thumb", "title")
    list_filter = ("placement", "is_active")
    search_fields = ("title", "heading", "eyebrow", "description")
    readonly_fields = ("large_preview", "mobile_preview", "created_display", "updated_display")
    ordering = ("placement", "order", "id")

    fieldsets = (
        (None, {
            "fields": (("title", "placement"),),
            "description": "«عنوان داخلی» فقط در پنل دیده می‌شود. محل نمایش تعیین می‌کند بنر در کدام بخش صفحهٔ اصلی قرار بگیرد.",
        }),
        ("متن بنر", {
            "fields": ("eyebrow", "heading", "description"),
        }),
        ("تصاویر", {
            "fields": (("image", "large_preview"), ("mobile_image", "mobile_preview"), "image_alt"),
            "description": "تصویر موبایل اختیاری است؛ اگر خالی باشد همان تصویر اصلی نمایش داده می‌شود.",
        }),
        ("دکمه", {
            "fields": (("button_text", "button_url"),),
        }),
        ("زمان‌بندی و نمایش", {
            "fields": (("starts_at", "ends_at"), ("is_active", "order"), ("created_display", "updated_display")),
            "description": "اگر زمان شروع یا پایان خالی باشد، محدودیتی در آن سمت وجود ندارد.",
        }),
    )

    @admin.display(description="تصویر")
    def thumb(self, obj):
        return image_preview(obj.image, 45)

    @admin.display(description="پیش‌نمایش")
    def large_preview(self, obj):
        return image_preview(obj.image if obj.pk else None, 160, 12)

    @admin.display(description="پیش‌نمایش موبایل")
    def mobile_preview(self, obj):
        return image_preview(obj.mobile_image if obj.pk else None, 160, 12)

    @admin.display(description="وضعیت نمایش")
    def schedule_status(self, obj):
        now = timezone.now()
        if not obj.is_active:
            return badge("غیرفعال", "#666", "#eee")
        if obj.starts_at and obj.starts_at > now:
            return badge(f"زمان‌بندی‌شده از {jalali(obj.starts_at)}", "#8a5a00", "#fff3d6")
        if obj.ends_at and obj.ends_at < now:
            return badge("منقضی‌شده", "#b42318", "#fde8e8")
        if obj.ends_at:
            return badge(f"در حال نمایش تا {jalali(obj.ends_at)}", "#05603a", "#dcfae6")
        return badge("در حال نمایش", "#05603a", "#dcfae6")

    @admin.display(description="تاریخ ایجاد")
    def created_display(self, obj):
        return jalali(obj.created_at) if obj.pk else "—"

    @admin.display(description="آخرین ویرایش")
    def updated_display(self, obj):
        return jalali(obj.updated_at) if obj.pk else "—"


# ---------------------------------------------------------------------- #
# مزیت‌ها، آمار و سؤالات متداول
# ---------------------------------------------------------------------- #
ICON_HELP = format_html(
    'نام آیکون از <a href="https://fonts.google.com/icons" target="_blank">Material Symbols</a>؛ '
    "مثلاً local_shipping یا verified_user"
)


@admin.register(StoreFeature)
class StoreFeatureAdmin(BaseContentAdmin):
    list_display = ("icon_display", "title", "description", "order", "is_active")
    list_display_links = ("icon_display", "title")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    readonly_fields = ("icon_display",)
    fieldsets = (
        (None, {"fields": ("title", "description")}),
        ("آیکون", {"fields": (("icon", "icon_display"),), "description": ICON_HELP}),
        ("نمایش", {"fields": (("is_active", "order"),)}),
    )

    class Media:
        css = {"all": (MATERIAL_ICONS_CSS,)}

    @admin.display(description="آیکون")
    def icon_display(self, obj):
        return icon_preview(obj.icon)


@admin.register(HomeStatistic)
class HomeStatisticAdmin(BaseContentAdmin):
    list_display = ("icon_display", "title", "value_display", "order", "is_active")
    list_display_links = ("icon_display", "title")
    list_filter = ("is_active",)
    search_fields = ("title", "value", "suffix")
    readonly_fields = ("icon_display",)
    fieldsets = (
        (None, {"fields": ("title", ("value", "suffix"))}),
        ("آیکون", {"fields": (("icon", "icon_display"),), "description": ICON_HELP}),
        ("نمایش", {"fields": (("is_active", "order"),)}),
    )

    class Media:
        css = {"all": (MATERIAL_ICONS_CSS,)}

    @admin.display(description="آیکون")
    def icon_display(self, obj):
        return icon_preview(obj.icon)

    @admin.display(description="مقدار", ordering="value")
    def value_display(self, obj):
        return format_html("<strong>{}</strong> {}", fa_num(obj.value), obj.suffix)


@admin.register(HomeFAQ)
class HomeFAQAdmin(BaseContentAdmin):
    list_display = ("question", "answer_preview", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    fields = ("question", "answer", ("is_active", "order"))

    @admin.display(description="خلاصهٔ پاسخ")
    def answer_preview(self, obj):
        text = obj.answer or ""
        return text[:90] + ("…" if len(text) > 90 else "")