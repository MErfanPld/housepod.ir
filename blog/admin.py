from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active", "post_count", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("order", "is_active")
    ordering = ("order", "name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "description"),
        }),
        ("تنظیمات نمایش", {
            "fields": ("is_active", "order"),
        }),
        ("اطلاعات زمانی", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = "تعداد مقالات"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at",)

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = "تعداد مقالات"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "is_featured",
        "views_count",
        "published_at",
        "created_at",
    )
    list_filter = (
        "status",
        "is_featured",
        "category",
        "tags",
        "published_at",
        "created_at",
    )
    search_fields = ("title", "slug", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("status", "is_featured")
    filter_horizontal = ("tags",)
    autocomplete_fields = ("category", "author")
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-created_at")
    list_per_page = 20
    readonly_fields = ("views_count", "created_at", "updated_at")

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "title",
                "slug",
                "category",
                "tags",
                "author",
                "excerpt",
                "content",
                "image",
            ),
        }),
        ("وضعیت انتشار", {
            "fields": (
                "status",
                "is_featured",
                "published_at",
            ),
        }),
        ("آمار و زمان", {
            "fields": ("views_count", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
