from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import BankAccount, Cart, CartItem, Order, OrderItem, PaymentReceipt


def receipt_preview(obj, max_height):
    """پیش‌نمایش فیش در ادمین؛ برای PDF لینک نمایش می‌دهد."""
    if not obj or not obj.image:
        return "—"
    if obj.image.name.lower().endswith(".pdf"):
        return format_html('<a href="{}" target="_blank">📄 مشاهدهٔ PDF</a>', obj.image.url)
    return format_html(
        '<a href="{}" target="_blank"><img src="{}" style="max-height:{}px;"/></a>',
        obj.image.url, obj.image.url, max_height,
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_items_display", "updated_at")
    search_fields = ("user__phone", "session_key")
    inlines = [CartItemInline]

    @admin.display(description="تعداد")
    def total_items_display(self, obj):
        return obj.total_items


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("title", "owner_name", "card_number", "bank_name", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "line_total",
    )
    can_delete = False


class PaymentReceiptInline(admin.TabularInline):
    model = PaymentReceipt
    extra = 0
    readonly_fields = ("image_preview", "uploaded_at", "tracking_code", "amount", "status")
    fields = (
        "image_preview",
        "image",
        "tracking_code",
        "amount",
        "status",
        "admin_note",
        "uploaded_at",
    )

    @admin.display(description="پیشنمایش")
    def image_preview(self, obj):
        return receipt_preview(obj, 80)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "total",
        "receiver_name",
        "city",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = (
        "order_number",
        "user__phone",
        "receiver_name",
        "receiver_phone",
        "city",
    )
    readonly_fields = ("order_number", "created_at", "updated_at", "paid_at", "subtotal", "total")
    inlines = [OrderItemInline, PaymentReceiptInline]
    actions = ("confirm_payment", "reject_payment", "mark_shipped")
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {
            "fields": (
                "order_number",
                "user",
                "status",
                "payment_method",
                "bank_account",
            ),
        }),
        ("آدرس ارسال", {
            "fields": (
                "receiver_name",
                "receiver_phone",
                "province",
                "city",
                "postal_code",
                "address",
            ),
        }),
        ("مبالغ", {
            "fields": ("subtotal", "shipping_cost", "total"),
        }),
        ("یادداشت", {
            "fields": ("user_note", "admin_note"),
        }),
        ("زمانها", {
            "fields": ("created_at", "updated_at", "paid_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.action(description="تأیید پرداخت و فیش")
    def confirm_payment(self, request, queryset):
        updated = 0
        for order in queryset:
            order.mark_confirmed()
            order.receipts.filter(status=PaymentReceipt.Status.PENDING).update(
                status=PaymentReceipt.Status.APPROVED,
                reviewed_at=timezone.now(),
                reviewed_by=request.user,
            )
            updated += 1
        self.message_user(request, f"{updated} سفارش تأیید شد.", messages.SUCCESS)

    @admin.action(description="رد فیش / پرداخت ناموفق")
    def reject_payment(self, request, queryset):
        updated = 0
        for order in queryset:
            order.mark_rejected()
            order.receipts.filter(status=PaymentReceipt.Status.PENDING).update(
                status=PaymentReceipt.Status.REJECTED,
                reviewed_at=timezone.now(),
                reviewed_by=request.user,
            )
            updated += 1
        self.message_user(request, f"{updated} سفارش رد شد.", messages.WARNING)

    @admin.action(description="علامتگذاری بهعنوان ارسالشده")
    def mark_shipped(self, request, queryset):
        n = queryset.filter(
            status__in=[Order.Status.CONFIRMED, Order.Status.PROCESSING]
        ).update(status=Order.Status.SHIPPED)
        self.message_user(request, f"{n} سفارش ارسال شد.", messages.SUCCESS)


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "status",
        "amount",
        "tracking_code",
        "uploaded_at",
        "reviewed_by",
        "thumb",
    )
    list_filter = ("status", "uploaded_at")
    search_fields = ("order__order_number", "tracking_code")
    readonly_fields = ("uploaded_at", "thumb")
    actions = ("approve_receipts", "reject_receipts")

    @admin.display(description="فیش")
    def thumb(self, obj):
        return receipt_preview(obj, 50)

    @admin.action(description="تأیید فیشهای انتخابشده")
    def approve_receipts(self, request, queryset):
        for receipt in queryset.select_related("order"):
            receipt.status = PaymentReceipt.Status.APPROVED
            receipt.reviewed_at = timezone.now()
            receipt.reviewed_by = request.user
            receipt.save()
            receipt.order.mark_confirmed()
        self.message_user(request, "فیشها تأیید شدند.", messages.SUCCESS)

    @admin.action(description="رد فیشهای انتخابشده")
    def reject_receipts(self, request, queryset):
        for receipt in queryset.select_related("order"):
            receipt.status = PaymentReceipt.Status.REJECTED
            receipt.reviewed_at = timezone.now()
            receipt.reviewed_by = request.user
            receipt.save()
            receipt.order.mark_rejected()
        self.message_user(request, "فیشها رد شدند.", messages.WARNING)