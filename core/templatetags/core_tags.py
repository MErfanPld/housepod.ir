from decimal import Decimal, InvalidOperation

from django import template
from django.http import QueryDict
from django.utils import timezone
from django.utils.html import strip_tags

register = template.Library()

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def fa_num(value):
    """تبدیل ارقام لاتین به فارسی: 1300 → ۱۳۰۰"""
    if value is None:
        return ""
    return str(value).translate(_FA_DIGITS)


@register.filter
def toman(value):
    """قالب‌بندی قیمت با جداکننده و ارقام فارسی: 1890000 → ۱,۸۹۰,۰۰۰"""
    if value in (None, ""):
        return ""
    try:
        number = int(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return fa_num(value)
    return f"{number:,}".translate(_FA_DIGITS)


@register.filter
def reading_time(text, words_per_minute=200):
    """زمان تقریبی مطالعه (دقیقه) بر اساس تعداد کلمات متن."""
    words = len(strip_tags(text or "").split())
    return max(1, round(words / int(words_per_minute)))


# ---------------------------------------------------------------------- #
# تاریخ شمسی (بدون وابستگی خارجی)
# ---------------------------------------------------------------------- #
_JALALI_MONTHS = (
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
)


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 + gd + g_d_m[gm - 1])
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


@register.filter
def jalali(value, fmt="long"):
    """تاریخ شمسی: long → «۱۵ آبان ۱۴۰۵» ، short → «۱۴۰۵/۰۸/۱۵»"""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    if fmt == "short":
        return f"{jy}/{jm:02d}/{jd:02d}".translate(_FA_DIGITS)
    return f"{jd} {_JALALI_MONTHS[jm - 1]} {jy}".translate(_FA_DIGITS)


# ---------------------------------------------------------------------- #
# کوئری‌استرینگ (برای صفحه‌بندی و فیلترها)
# ---------------------------------------------------------------------- #
@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    """
    پارامترهای GET فعلی را نگه می‌دارد و فقط موارد داده‌شده را عوض می‌کند.
    مقدار خالی یعنی حذف پارامتر.  مثال: ?{% query_replace page=3 %}
    """
    request = context.get("request")
    query = request.GET.copy() if request else QueryDict(mutable=True)
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return query.urlencode()