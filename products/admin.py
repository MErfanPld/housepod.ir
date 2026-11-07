from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "order",
        "is_active",
        "product_count",
        "created_at",
    )

    list_filter = (
        "is_active",
        "parent",
        "gradient",
    )

    search_fields = (
        "name",
        "slug",
        "english_name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = (
        "order",
        "is_active",
    )

    list_per_page = 25
    ordering = ("order", "name")
    list_select_related = ("parent",)
    date_hierarchy = "created_at"

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "name",
                "slug",
                "english_name",
                "parent",
                "description",
                "image",
            ),
        }),
        ("تنظیمات نمایش کارت", {
            "fields": (
                "badge_text",
                "gradient",
                "link_text",
            ),
        }),
        ("وضعیت و ترتیب", {
            "fields": (
                "is_active",
                "order",
            ),
        }),
        ("اطلاعات زمانی", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="تعداد محصولات", ordering="products__count")
    def product_count(self, obj):
        return obj.products.count()

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt", "order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "sku",
        "brand",
        "price_display",
        "stock",
        "compatibility",
        "is_active",
        "is_featured",
        "is_available",
        "created_at",
    )
    list_filter = (
        "category",
        "brand",
        "compatibility",
        "is_active",
        "is_featured",
        "is_available",
        "created_at",
    )
    search_fields = ("name", "name_en", "sku", "slug", "flavor", "short_description", "brand")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("stock", "is_active", "is_featured", "is_available")
    readonly_fields = ("created_at", "updated_at", "final_price_display")
    autocomplete_fields = ("category",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [ProductImageInline]

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "category",
                "name",
                "name_en",
                "slug",
                "sku",
                "brand",
                "short_description",
                "description",
            ),
        }),
        ("قیمت و موجودی", {
            "fields": (
                "price",
                "discount_price",
                "final_price_display",
                "stock",
            ),
        }),
        ("مشخصات محصول", {
            "fields": (
                "flavor",
                "compatibility",
                "badge_1",
                "badge_2",
                "badge_3",
                "specs",
                "usage_guide",
                "image",
            ),
        }),
        ("امتیاز و نظرات", {
            "fields": ("rating", "reviews_count"),
        }),
        ("وضعیت نمایش", {
            "fields": (
                "is_active",
                "is_available",
                "is_featured",
            ),
        }),
        ("اطلاعات زمانی", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def price_display(self, obj):
        if obj.pk is None or obj.price is None:
            return "—"
        if obj.has_discount and obj.discount_price is not None:
            return format_html(
                '<span style="text-decoration: line-through; color: #888;">{}</span> '
                '<strong style="color: #c00;">{}</strong> تومان',
                f"{obj.price:,.0f}",
                f"{obj.discount_price:,.0f}",
            )
        return f"{obj.price:,.0f} تومان"
    price_display.short_description = "قیمت"

    def final_price_display(self, obj):
        if obj.pk is None or obj.price is None:
            return "— (بعد از ذخیره محاسبه می‌شود)"
        final = obj.final_price
        if final is None:
            return "—"
        return f"{final:,.0f} تومان"
    final_price_display.short_description = "قیمت نهایی"