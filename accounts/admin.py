from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = (
        "title",
        "receiver_name",
        "receiver_phone",
        "province",
        "city",
        "postal_code",
        "is_default",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "phone",
        "get_full_name",
        "is_profile_complete",
        "is_phone_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_profile_complete",
        "is_phone_verified",
        "date_joined",
    )
    search_fields = ("phone", "first_name", "last_name", "email", "national_code")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "updated_at", "last_login")
    inlines = [AddressInline]

    fieldsets = (
        (None, {
            "fields": ("phone", "password"),
        }),
        ("اطلاعات شخصی", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "national_code",
            ),
        }),
        ("آدرس ارسال پیش‌فرض", {
            "fields": (
                "province",
                "city",
                "postal_code",
                "address",
                "receiver_name",
                "receiver_phone",
            ),
        }),
        ("وضعیت", {
            "fields": (
                "is_phone_verified",
                "is_profile_complete",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("زمان‌ها", {
            "fields": ("last_login", "date_joined", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name() or "—"
    get_full_name.short_description = "نام کامل"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "receiver_name",
        "city",
        "province",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default", "province", "city")
    search_fields = ("title", "receiver_name", "receiver_phone", "user__phone", "city")
    autocomplete_fields = ("user",)
