from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

SUCCESS = {"confirmed", "processing", "shipped", "delivered"}
DANGER = {"rejected", "cancelled"}

# ترتیب وضعیت‌ها برای تایم‌لاین
_FLOW = ["pending_payment", "awaiting_verify", "confirmed", "processing", "shipped", "delivered"]


@register.filter
def status_tone(status):
    """رنگ وضعیت سفارش/فیش: success | danger | warning"""
    if status in SUCCESS or status in {"approved", "verified"}:
        return "success"
    if status in DANGER:
        return "danger"
    return "warning"


@register.filter
def status_icon(status):
    return {
        "pending_payment": "account_balance_wallet",
        "awaiting_verify": "hourglass_top",
        "confirmed": "check_circle",
        "processing": "inventory_2",
        "shipped": "local_shipping",
        "delivered": "task_alt",
        "rejected": "error",
        "cancelled": "cancel",
    }.get(status, "receipt_long")


@register.filter
def is_pdf(file_field):
    """آیا فایل آپلودشده PDF است؟ (برای نمایش لینک به‌جای تصویر)"""
    name = getattr(file_field, "name", "") or ""
    return name.lower().endswith(".pdf")


@register.filter
def to_rial(value):
    """تومان → ریال با جداکننده و ارقام فارسی"""
    try:
        number = int(Decimal(str(value)) * 10)
    except (InvalidOperation, ValueError, TypeError):
        return ""
    return f"{number:,}".translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


@register.simple_tag
def order_timeline(order):
    """
    مراحل سفارش با وضعیت هر مرحله: done | current | failed | upcoming
    """
    status = order.status
    steps = [
        ("ثبت سفارش", "سفارش ثبت و اقلام رزرو شد.", "receipt_long"),
        ("ارسال فیش پرداخت", "تصویر فیش واریزی بارگذاری می‌شود.", "upload_file"),
        ("بررسی و تأیید پرداخت", "فیش با گردش حساب تطبیق داده می‌شود.", "fact_check"),
        ("آماده‌سازی و بسته‌بندی", "سلامت کالا بررسی و بسته‌بندی می‌شود.", "inventory_2"),
        ("ارسال سفارش", "مرسوله تحویل پست / پیک شده است.", "local_shipping"),
        ("تحویل به مشتری", "سفارش به دست شما رسید.", "task_alt"),
    ]

    if status == "cancelled":
        result = [{"title": t, "desc": d, "icon": i, "state": "upcoming"} for t, d, i in steps]
        result[0]["state"] = "done"
        result[1] = {"title": "سفارش لغو شد", "desc": "این سفارش لغو شده است.", "icon": "cancel", "state": "failed"}
        return result[:2]

    if status == "rejected":
        current_index, failed = 2, True
    else:
        # pending_payment → مرحلهٔ ۱ (ارسال فیش) جاری است
        position = {"pending_payment": 1, "awaiting_verify": 2, "confirmed": 3,
                    "processing": 3, "shipped": 4, "delivered": 6}
        current_index, failed = position.get(status, 1), False

    result = []
    for index, (title, desc, icon) in enumerate(steps):
        if index < current_index:
            state = "done"
        elif index == current_index:
            state = "failed" if failed else "current"
        else:
            state = "upcoming"
        if failed and index == current_index:
            title, desc, icon = "فیش رد شد", "لطفاً فیش معتبر را دوباره بارگذاری کنید‌‌.", "error"
        result.append({"title": title, "desc": desc, "icon": icon, "state": state})
    return result