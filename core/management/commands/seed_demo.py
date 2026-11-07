"""
ساخت داده‌های نمونهٔ واقعی (۴ رکورد برای هر مدل) برای صفحهٔ خانه.

اجرا:
    python manage.py seed_demo            # ساخت / به‌روزرسانی داده‌ها
    python manage.py seed_demo --clear    # حذف داده‌های قبلی همین مدل‌ها و ساخت مجدد

اجرای چندباره امن است: رکوردها با کلید یکتا (slug / sku / عنوان) به‌روزرسانی می‌شوند
و تصویرها فقط وقتی ساخته می‌شوند که رکورد تصویر نداشته باشد.
"""

from datetime import timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from blog.models import Category as BlogCategory
from blog.models import Post, Tag
from core.models import HeroSlide, HomeBanner, HomeFAQ, HomeStatistic, StoreFeature
from products.models import Category, Product, ProductImage

ZW = "‌"  # نیم‌فاصله


# ---------------------------------------------------------------------- #
# Image helper
# ---------------------------------------------------------------------- #
def _font(size):
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def make_image(filename, label, colors, size=(800, 1000), sublabel=""):
    """تصویر گرادیانی با متن لاتین (برای فیلدهای ImageField)."""
    width, height = size
    top, bottom = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in colors)
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)

    # یک دایرهٔ نورانی پشت متن
    r = min(width, height) // 3
    cx, cy = width // 2, height // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)

    title_font = _font(max(28, width // 14))
    sub_font = _font(max(18, width // 28))
    box = draw.textbbox((0, 0), label, font=title_font)
    draw.text(((width - (box[2] - box[0])) / 2, cy - (box[3] - box[1]) / 2 - 10),
              label, fill=(255, 255, 255), font=title_font)
    if sublabel:
        box = draw.textbbox((0, 0), sublabel, font=sub_font)
        draw.text(((width - (box[2] - box[0])) / 2, cy + r * 0.45),
                  sublabel, fill=(230, 230, 230), font=sub_font)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return ContentFile(buffer.getvalue(), name=filename)


def attach_image(obj, field, filename, label, colors, size=(800, 1000), sublabel=""):
    """فقط اگر فیلد تصویر خالی است، تصویر بساز و ذخیره کن."""
    file_field = getattr(obj, field)
    if not file_field:
        file_field.save(filename, make_image(filename, label, colors, size, sublabel), save=True)


def resolve_url(value):
    """'category:<slug>' و 'product_list' را به آدرس واقعی تبدیل می‌کند؛ بقیه دست‌نخورده."""
    if value.startswith("category:"):
        category = Category.objects.filter(slug=value.split(":", 1)[1]).first()
        return category.get_absolute_url() if category else "#categories"
    if value == "product_list":
        try:
            return reverse("products:product_list")
        except NoReverseMatch:
            return "#catalog"
    return value


# ---------------------------------------------------------------------- #
# Data
# ---------------------------------------------------------------------- #
PRODUCT_CATEGORIES = [
    {
        "slug": "pod-systems",
        "name": "پاد سیستم",
        "english_name": "Pod Systems",
        "description": f"پاد سیستم{ZW}های جمع{ZW}وجور با کارتریج قابل تعویض از برندهای OXVA، Vaporesso و Geekvape.",
        "badge_text": "۴۸ مدل فعال",
        "gradient": "purple",
        "link_text": f"مشاهده مدل{ZW}ها",
        "order": 1,
        "colors": ("#6A1FE9", "#3B1187"),
    },
    {
        "slug": "iqos-devices",
        "name": f"دستگاه{ZW}های IQOS",
        "english_name": "IQOS Heated Tobacco",
        "description": "سری ILUMA با فناوری گرمایش القایی SMARTCORE، بدون تیغه و بدون نیاز به تمیزکاری.",
        "badge_text": "اصالت تضمینی",
        "gradient": "charcoal",
        "link_text": f"مشاهده دستگاه{ZW}ها",
        "order": 2,
        "colors": ("#261E1A", "#FF5B26"),
    },
    {
        "slug": "cartridges-coils",
        "name": "کارتریج و کویل",
        "english_name": "Cartridges & Coils",
        "description": f"کارتریج{ZW}های اورجینال با مقاومت{ZW}های مختلف برای انواع پاد سیستم.",
        "badge_text": "+۱۲۰ مدل",
        "gradient": "magenta",
        "link_text": f"مشاهده کارتریج{ZW}ها",
        "order": 3,
        "colors": ("#D92A8E", "#7E1352"),
    },
    {
        "slug": "accessories",
        "name": f"لوازم جانبی",
        "english_name": "Accessories",
        "description": f"کاور، بند گردنی، کابل فست{ZW}شارژ و کیف{ZW}های محافظ.",
        "badge_text": "ارسال رایگان",
        "gradient": "cyan",
        "link_text": f"مشاهده اکسسوری{ZW}ها",
        "order": 4,
        "colors": ("#0FAFCF", "#124974"),
    },
]

PRODUCTS = [
    {
        "sku": "OXV-XLP2-BLK",
        "category": "pod-systems",
        "name": f"پاد سیستم اکسوا ایکسلیم پرو ۲",
        "name_en": "OXVA Xlim Pro 2 Pod Kit • 30W Maximum Output",
        "brand": "OXVA",
        "short_description": f"بدنهٔ آلیاژ روی، نمایشگر رنگی و کنترل دقیق جریان هوا با باتری ۱۳۰۰ میلی{ZW}آمپر.",
        "description": (
            f"ایکسلیم پرو ۲ نسل جدید پاد سیستم{ZW}های اکسوا است که با بدنهٔ مستحکم آلیاژ روی و "
            f"نمایشگر HD، اطلاعات توان، باتری و تعداد پاف را نمایش می{ZW}دهد. سیستم تنظیم جریان هوا "
            f"به شما اجازه می{ZW}دهد بین کشش دهانی و ریه{ZW}ای جابه{ZW}جا شوید."
        ),
        "specs": (
            f"ظرفیت باتری|۱۳۰۰ میلی{ZW}آمپر\n"
            "حداکثر توان|۳۰ وات\n"
            f"ظرفیت کارتریج|۲ میلی{ZW}لیتر\n"
            "نوع شارژ|Type-C فست\n"
            "جنس بدنه|آلیاژ روی"
        ),
        "usage_guide": f"قبل از اولین استفاده، کارتریج را پر کرده و ۵ دقیقه صبر کنید تا پنبه کاملاً اشباع شود.",
        "badge_1": "1300 mAh",
        "badge_2": f"۳۰W توان خروجی",
        "badge_3": "شارژ Type-C",
        "price": 2150000,
        "discount_price": 1890000,
        "stock": 14,
        "compatibility": Product.DeviceCompatibility.OTHER,
        "rating": 4.7,
        "reviews_count": 86,
        "is_featured": True,
        "colors": ("#1F1A2E", "#93CA18"),
        "days_ago": 3,
    },
    {
        "sku": "IQS-ILM1-GRY",
        "category": "iqos-devices",
        "name": f"دستگاه آیکاس ایلوما وان",
        "name_en": "IQOS ILUMA ONE All-in-One",
        "brand": "IQOS",
        "short_description": f"دستگاه یکپارچهٔ ایلوما با فناوری SMARTCORE و ۲۰ استفادهٔ پیاپی با یک شارژ.",
        "description": (
            f"ایلوما وان ساده{ZW}ترین عضو خانوادهٔ ILUMA است. گرمایش القایی از داخل استیک، "
            f"نیاز به تیغه و تمیزکاری را از بین برده و طعم یکنواختی از اولین تا آخرین کام ارائه می{ZW}دهد."
        ),
        "specs": (
            "فناوری گرمایش|SMARTCORE INDUCTION\n"
            f"تعداد استفاده با هر شارژ|۲۰ عدد\n"
            f"زمان شارژ کامل|۹۰ دقیقه\n"
            f"سازگاری|استیک{ZW}های TEREA"
        ),
        "usage_guide": f"فقط از استیک{ZW}های TEREA استفاده کنید؛ استفاده از سایر استیک{ZW}ها به دستگاه آسیب می{ZW}زند.",
        "badge_1": "Smartcore",
        "badge_2": f"۲۰ استفاده پیاپی",
        "badge_3": "بدون تیغه",
        "price": 2950000,
        "discount_price": 2590000,
        "stock": 2,
        "compatibility": Product.DeviceCompatibility.ILUMA_ONE,
        "rating": 4.9,
        "reviews_count": 142,
        "is_featured": True,
        "colors": ("#3A3532", "#FF5B26"),
        "days_ago": 10,
    },
    {
        "sku": "VPR-XRS4-SLV",
        "category": "pod-systems",
        "name": f"پاد سیستم ویپرسو اکسراس ۴",
        "name_en": "Vaporesso XROS 4 Pod Kit",
        "brand": "VAPORESSO",
        "short_description": f"فناوری COREX 2.0، سه حالت خروجی و بدنهٔ آلومینیوم آیروسپیس.",
        "description": (
            f"اکسراس ۴ با پلتفرم COREX 2.0 طعم{ZW}رسانی دقیق{ZW}تر و عمر کارتریج بیشتری دارد. "
            f"سه حالت خروجی ECO، NORM و BOOST انعطاف کامل در مصرف باتری فراهم می{ZW}کند."
        ),
        "specs": (
            f"ظرفیت باتری|۱۰۰۰ میلی{ZW}آمپر\n"
            "حداکثر توان|۳۰ وات\n"
            "فناوری کویل|COREX 2.0\n"
            "حالت خروجی|ECO / NORM / BOOST"
        ),
        "usage_guide": f"برای افزایش عمر کویل، بین کام{ZW}ها چند ثانیه فاصله بگذارید.",
        "badge_1": "1000 mAh",
        "badge_2": "Corex 2.0",
        "badge_3": f"۳ حالت خروجی",
        "price": 1980000,
        "discount_price": None,
        "stock": 27,
        "compatibility": Product.DeviceCompatibility.OTHER,
        "rating": 4.6,
        "reviews_count": 64,
        "is_featured": True,
        "colors": ("#0FAFCF", "#1C2B4A"),
        "days_ago": 18,
    },
    {
        "sku": "GKV-WQP-GUN",
        "category": "pod-systems",
        "name": f"پاد سیستم گیک{ZW}ویپ ونکس کیو پرو",
        "name_en": "Geekvape Wenax Q Pro Pod Kit",
        "brand": "GEEKVAPE",
        "short_description": f"بدنهٔ گان{ZW}متال، اسلایدر جریان هوا و لرزش هوشمند هپتیک.",
        "description": (
            f"ونکس کیو پرو با اسلایدر لمسی جریان هوا و بازخورد لرزشی، تجربهٔ کاربری متفاوتی می{ZW}سازد. "
            f"باتری ۱۲۰۰ میلی{ZW}آمپر به{ZW}راحتی یک روز کامل کار می{ZW}کند."
        ),
        "specs": (
            f"ظرفیت باتری|۱۲۰۰ میلی{ZW}آمپر\n"
            "حداکثر توان|۲۵ وات\n"
            "نمایشگر|۰.۴۹ اینچ OLED\n"
            "جنس بدنه|آلیاژ روی گان‌متال"
        ),
        "usage_guide": f"برای قفل کردن دستگاه، دکمه را ۵ بار پشت سر هم فشار دهید.",
        "badge_1": "1200 mAh",
        "badge_2": "Haptic Touch",
        "badge_3": "OLED",
        "price": 2200000,
        "discount_price": 1950000,
        "stock": 9,
        "compatibility": Product.DeviceCompatibility.OTHER,
        "rating": 4.4,
        "reviews_count": 31,
        "is_featured": False,
        "colors": ("#2B2B33", "#6A1FE9"),
        "days_ago": 1,
    },
]

BLOG_CATEGORIES = [
    ("buying-guide", f"راهنمای خرید", 1),
    ("technical-review", "بررسی فنی", 2),
    ("maintenance", f"نگهداری و تعمیر", 3),
    ("news", f"اخبار و تازه{ZW}ها", 4),
]

TAGS = [
    ("pod-system", f"پاد سیستم"),
    ("iqos", "IQOS"),
    ("coil", "کویل"),
    ("beginner", f"مبتدی"),
]

POSTS = [
    {
        "slug": "best-pod-system-for-beginners",
        "title": f"راهنمای انتخاب بهترین پاد سیستم برای شروع",
        "category": "buying-guide",
        "tags": ["pod-system", "beginner"],
        "excerpt": (
            f"اگر قصد ورود به دنیای پاد سیستم{ZW}ها را دارید، بررسی توان دستگاه، مقاومت کویل{ZW}ها "
            f"و نحوهٔ تنظیم جریان هوا کلیدی{ZW}ترین موارد هستند."
        ),
        "content": (
            f"انتخاب اولین پاد سیستم می{ZW}تواند گیج{ZW}کننده باشد. در این راهنما سه معیار اصلی را بررسی می{ZW}کنیم.\n\n"
            f"۱. ظرفیت باتری: برای استفادهٔ روزانه، باتری ۱۰۰۰ میلی{ZW}آمپر یا بیشتر انتخاب مناسبی است.\n\n"
            f"۲. مقاومت کویل: کویل{ZW}های بالای ۱ اهم برای کشش دهانی (MTL) و کویل{ZW}های زیر ۱ اهم برای کشش ریه{ZW}ای مناسب{ZW}اند.\n\n"
            f"۳. تنظیم جریان هوا: دستگاهی انتخاب کنید که امکان تنظیم ایرفلو داشته باشد تا بتوانید کشش را مطابق سلیقه{ZW}تان تغییر دهید.\n\n"
            f"در نهایت، از خرید دستگاه بدون کد اصالت خودداری کنید و همیشه از کارتریج{ZW}های اورجینال استفاده کنید."
        ),
        "is_featured": True,
        "views": 1240,
        "days_ago": 4,
        "colors": ("#6A1FE9", "#0FAFCF"),
    },
    {
        "slug": "iluma-vs-previous-iqos",
        "title": f"تفاوت{ZW}های کلیدی سری ایلوما با نسل{ZW}های قبلی آیکاس",
        "category": "technical-review",
        "tags": ["iqos"],
        "excerpt": (
            f"فناوری القایی جدید چگونه نیاز به تمیز کردن مداوم تیغه را حذف کرده و عملکردی پایدار ارائه می{ZW}دهد؟"
        ),
        "content": (
            f"نسل{ZW}های قبلی آیکاس برای گرم کردن تنباکو از یک تیغهٔ سرامیکی استفاده می{ZW}کردند که باید مرتب تمیز می{ZW}شد.\n\n"
            f"در سری ILUMA، یک قطعهٔ فلزی داخل خود استیک TEREA قرار دارد و دستگاه با میدان مغناطیسی آن را از داخل گرم می{ZW}کند. "
            f"نتیجه: بدون تیغه، بدون باقی{ZW}مانده و بدون نیاز به تمیزکاری.\n\n"
            f"نکتهٔ مهم این است که استیک{ZW}های HEETS با ایلوما سازگار نیستند و فقط باید از TEREA استفاده شود.\n\n"
            f"از نظر عمر باتری، ایلوما پرایم و ایلوما استاندارد هر کدام حدود ۲۰ استیک با یک شارژ کامل پشتیبانی می{ZW}کنند."
        ),
        "is_featured": True,
        "views": 980,
        "days_ago": 9,
        "colors": ("#261E1A", "#FF5B26"),
    },
    {
        "slug": "extend-coil-and-cartridge-life",
        "title": f"۵ نکتهٔ اساسی برای افزایش طول عمر کارتریج و کویل",
        "category": "maintenance",
        "tags": ["coil", "pod-system"],
        "excerpt": (
            f"از آماده{ZW}سازی صحیح کارتریج در بار اول تا جلوگیری از کام{ZW}گیری متوالی؛ ترفندهایی مؤثر برای حفظ کیفیت طعم."
        ),
        "content": (
            f"۱. کارتریج نو را پر کنید و ۵ تا ۱۰ دقیقه صبر کنید تا پنبه کاملاً خیس شود.\n\n"
            f"۲. در چند کام اول، توان را پایین نگه دارید.\n\n"
            f"۳. از کام{ZW}گیری پشت سر هم پرهیز کنید تا پنبه فرصت بازجذب مایع داشته باشد.\n\n"
            f"۴. اجازه ندهید سطح مایع از حد مشخص{ZW}شده پایین{ZW}تر برود.\n\n"
            f"۵. مایع{ZW}های با شیرینی کمتر، رسوب کمتری روی کویل ایجاد می{ZW}کنند."
        ),
        "is_featured": False,
        "views": 615,
        "days_ago": 15,
        "colors": ("#D92A8E", "#7E1352"),
    },
    {
        "slug": "new-arrivals-autumn",
        "title": f"تازه{ZW}های پاییز؛ معرفی محصولات جدید فروشگاه",
        "category": "news",
        "tags": ["pod-system", "iqos"],
        "excerpt": f"نگاهی سریع به دستگاه{ZW}هایی که در پارت جدید به انبار رسیده{ZW}اند و ویژگی{ZW}های شاخص هرکدام.",
        "content": (
            f"در پارت جدید، مدل{ZW}های ونکس کیو پرو، اکسراس ۴ و ایلوما وان به انبار اضافه شدند.\n\n"
            f"ونکس کیو پرو با اسلایدر جریان هوا و بازخورد لرزشی، گزینهٔ جذابی برای کاربران حرفه{ZW}ای است. "
            f"اکسراس ۴ با فناوری COREX 2.0 طعم{ZW}رسانی بهتری دارد و ایلوما وان ساده{ZW}ترین راه ورود به دنیای IQOS است.\n\n"
            f"موجودی برخی مدل{ZW}ها محدود است؛ برای اطلاع از موجودی مجدد، گزینهٔ «اطلاع{ZW}رسانی موجودی» را فعال کنید."
        ),
        "is_featured": False,
        "views": 402,
        "days_ago": 1,
        "colors": ("#93CA18", "#204907"),
    },
]

HERO_SLIDES = [
    {
        "title_line1": f"دنیای دستگاه{ZW}های",
        "title_highlight": "نسل جدید",
        "badge_text": f"کالکشن جدید پاییز ۱۴۰۵",
        "description": (
            f"جدیدترین پاد سیستم{ZW}ها و دستگاه{ZW}های IQOS را با ضمانت اصالت، ارسال اکسپرس "
            f"و مشاورهٔ تخصصی تهیه کنید."
        ),
        "primary_btn_text": f"مشاهده محصولات",
        "primary_btn_url": "#catalog",
        "secondary_btn_text": f"کشف دسته{ZW}بندی{ZW}ها",
        "secondary_btn_url": "#categories",
        "image_alt": f"پاد سیستم و دستگاه IQOS",
        "top_left_badge": f"کالکشن ویژه",
        "top_right_badge": "IQOS & OXVA PRO",
        "feature_title": f"تکنولوژی گرمایش هوشمند",
        "feature_subtitle": "IQOS ILUMA & POD X",
        "price_label": "شروع از",
        "price": "1,890,000",
        "order": 1,
        "label": "NEW GENERATION",
        "colors": ("#6A1FE9", "#D92A8E"),
    },
    {
        "title_line1": f"آیکاس ایلوما؛",
        "title_highlight": "بدون تیغه، بدون دود",
        "badge_text": "SMARTCORE INDUCTION",
        "description": f"گرمایش القایی از داخل استیک با طعمی یکنواخت و بدون نیاز به تمیزکاری.",
        "primary_btn_text": f"خرید آیکاس",
        "primary_btn_url": "category:iqos-devices",
        "secondary_btn_text": f"مقایسهٔ مدل{ZW}ها",
        "secondary_btn_url": "#faq",
        "image_alt": f"دستگاه آیکاس ایلوما وان",
        "top_left_badge": f"اصالت تضمینی",
        "top_right_badge": "ILUMA ONE",
        "feature_title": f"۲۰ استفادهٔ پیاپی",
        "feature_subtitle": f"شارژ کامل در ۹۰ دقیقه",
        "price_label": "قیمت",
        "price": "2,590,000",
        "order": 2,
        "label": "IQOS ILUMA",
        "colors": ("#261E1A", "#FF5B26"),
    },
    {
        "title_line1": f"تا ۱۵٪ تخفیف",
        "title_highlight": f"پاد سیستم{ZW}ها",
        "badge_text": f"فروش ویژهٔ هفته",
        "description": f"اکسوا، گیک{ZW}ویپ و ویپرسو با قیمت ویژه؛ فقط تا پایان موجودی.",
        "primary_btn_text": f"مشاهده تخفیف{ZW}ها",
        "primary_btn_url": "#catalog",
        "secondary_btn_text": "",
        "secondary_btn_url": "",
        "image_alt": f"پاد سیستم{ZW}های تخفیف{ZW}دار",
        "top_left_badge": f"تخفیف ویژه",
        "top_right_badge": "UP TO 15% OFF",
        "feature_title": f"ارسال رایگان",
        "feature_subtitle": f"خرید بالای ۳ میلیون تومان",
        "price_label": "شروع از",
        "price": "1,950,000",
        "order": 3,
        "label": "WEEKLY SALE",
        "colors": ("#0FAFCF", "#6A1FE9"),
    },
    {
        "title_line1": f"اکسسوری{ZW}های",
        "title_highlight": "استایل و محافظت",
        "badge_text": f"لوازم جانبی اورجینال",
        "description": f"کاور، بند گردنی، کیف چرمی دست{ZW}دوز و کابل{ZW}های فست{ZW}شارژ استاندارد.",
        "primary_btn_text": f"مشاهده اکسسوری{ZW}ها",
        "primary_btn_url": "category:accessories",
        "secondary_btn_text": "",
        "secondary_btn_url": "",
        "image_alt": f"لوازم جانبی پاد سیستم",
        "top_left_badge": "",
        "top_right_badge": "GENUINE",
        "feature_title": f"کیفیت تضمینی",
        "feature_subtitle": f"ضمانت ۷ روزه تعویض",
        "price_label": "شروع از",
        "price": "290,000",
        "order": 4,
        "label": "ACCESSORIES",
        "colors": ("#93CA18", "#0FAFCF"),
    },
]

BANNERS = [
    {
        "placement": HomeBanner.Placement.WIDE,
        "title": f"بنر عریض IQOS",
        "eyebrow": "SMARTCORE INDUCTION SYSTEM™",
        "heading": f"محصولات IQOS و تکنولوژی گرمایش هوشمند",
        "description": (
            f"مدل{ZW}ها و لوازم جانبی اورجینال را با جزئیات بررسی و مقایسه کنید. بدون تیغه، بدون خاکستر، "
            f"بدون دود و با حفظ اصالت طعم تنباکو به روش القایی."
        ),
        "button_text": f"مشاهده کالکشن کامل IQOS",
        "button_url": "category:iqos-devices",
        "label": "IQOS ILUMA PRIME",
        "colors": ("#1A1512", "#FF5B26"),
        "size": (900, 900),
    },
    {
        "placement": HomeBanner.Placement.PROMO_LEFT,
        "title": f"بنر پاد سیستم{ZW}ها",
        "eyebrow": f"انتخاب حرفه{ZW}ای{ZW}ها",
        "heading": f"دنیای پاد سیستم{ZW}ها؛\nطراحی باریک و کاربری آسان",
        "description": f"بررسی و مقایسهٔ جامع برترین برندهای بین{ZW}المللی همراه با گارانتی اصالت کالا.",
        "button_text": f"مشاهده مدل{ZW}ها",
        "button_url": "category:pod-systems",
        "label": "POD LAB",
        "colors": ("#2D164B", "#0FAFCF"),
        "size": (600, 600),
    },
    {
        "placement": HomeBanner.Placement.PROMO_RIGHT,
        "title": f"بنر اکسسوری{ZW}ها",
        "eyebrow": f"استایل و محافظت",
        "heading": f"اکسسوری{ZW}های موردنیازت؛\nکاور، بند و شارژرهای مدرن",
        "description": f"کیف{ZW}های چرمی دست{ZW}دوز، کابل{ZW}های فست{ZW}شارژ و محافظ{ZW}های ژله{ZW}ای ضدضربه.",
        "button_text": f"مشاهده اکسسوری{ZW}ها",
        "button_url": "category:accessories",
        "label": "ACCESSORIES",
        "colors": ("#D92A8E", "#FF5B26"),
        "size": (600, 600),
    },
    {
        "placement": HomeBanner.Placement.BOTTOM,
        "title": f"بنر ارسال رایگان",
        "eyebrow": f"فقط این هفته",
        "heading": f"ارسال رایگان برای خریدهای بالای ۳ میلیون تومان",
        "description": "",
        "button_text": f"شروع خرید",
        "button_url": "product_list",
        "label": "FREE SHIPPING",
        "colors": ("#6A1FE9", "#204907"),
        "size": (1400, 400),
    },
]

STORE_FEATURES = [
    ("ارسال سریع اکسپرس", f"تحویل همان روز در تهران", "local_shipping", 1),
    ("اصالت ۱۰۰٪ کالاها", f"کد اصالت{ZW}سنجی معتبر", "verified_user", 2),
    (f"پشتیبانی تخصصی", f"مشاورهٔ فنی ۷ روز هفته", "support_agent", 3),
    (f"ضمانت ۷ روزه تعویض", f"تضمین سلامت فیزیکی قطعات", "swap_horiz", 4),
]

STATISTICS = [
    (f"محصول اورجینال", "۲۰۰+", "مدل", "inventory_2", 1),
    (f"مشتری راضی", "۱۲,۵۰۰+", "نفر", "groups", 2),
    (f"برند معتبر", "۱۸", "برند", "workspace_premium", 3),
    (f"سال تجربه", "۶", "سال", "history", 4),
]

FAQS = [
    (
        f"چگونه مشخصات فنی دستگاه{ZW}ها را با یکدیگر مقایسه کنم؟",
        f"در صفحهٔ هر محصول، جدول تفکیک{ZW}شده{ZW}ای از ظرفیت باتری، نوع کارتریج، حداکثر توان خروجی و "
        f"سازگاری مقاومت{ZW}ها درج شده است. همچنین با دکمهٔ مقایسه می{ZW}توانید دو دستگاه را کنار هم قرار دهید.",
    ),
    (
        f"روش{ZW}ها و زمان{ZW}بندی ارسال سفارش به چه صورت است؟",
        f"برای تهران، سفارش{ZW}های ثبت{ZW}شده تا ساعت ۱۲ ظهر همان روز با پیک ویژه تحویل می{ZW}شوند. "
        f"برای شهرستان{ZW}ها، سفارش{ZW}ها از طریق پست پیشتاز یا تیپاکس ظرف ۲۴ تا ۴۸ ساعت کاری ارسال می{ZW}شوند.",
    ),
    (
        f"چگونه از موجودی مجدد یک کالا یا رنگ{ZW}بندی خاص مطلع شوم؟",
        f"در صورت اتمام موجودی، با کلیک روی گزینهٔ «اطلاع{ZW}رسانی موجودی» در صفحهٔ همان محصول، "
        f"به محض ورود بار جدید پیامک رایگان دریافت می{ZW}کنید.",
    ),
    (
        f"از چه طریقی می{ZW}توانم با کارشناس پشتیبانی صحبت کنم؟",
        f"تیم فنی همه{ZW}روزه از ساعت ۹ تا ۲۱ از طریق تماس تلفنی، چت آنلاین و تلگرام "
        f"آمادهٔ پاسخ به سؤالات فنی و راهنمایی قبل از خرید است.",
    ),
]


# ---------------------------------------------------------------------- #
# Command
# ---------------------------------------------------------------------- #
class Command(BaseCommand):
    help = "ساخت داده‌های نمونه (۴ رکورد برای هر مدل) برای صفحهٔ خانه"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="قبل از ساخت، تمام رکوردهای این مدل‌ها را حذف می‌کند.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self.clear()

        now = timezone.now()
        self.seed_product_categories()
        self.seed_products(now)
        self.seed_blog(now)
        self.seed_hero()
        self.seed_banners()
        self.seed_simple_models()

        self.stdout.write(self.style.SUCCESS("داده‌های نمونه با موفقیت ساخته شدند ✅"))

    # ------------------------------------------------------------------ #
    def clear(self):
        # ترتیب مهم است: Product → Category به خاطر PROTECT
        for model in (ProductImage, Product, Category, Post, Tag, BlogCategory,
                      HeroSlide, HomeBanner, StoreFeature, HomeStatistic, HomeFAQ):
            count, _ = model.objects.all().delete()
            self.stdout.write(f"  حذف {model._meta.verbose_name_plural}: {count}")

    def seed_product_categories(self):
        for data in PRODUCT_CATEGORIES:
            data = dict(data)
            colors = data.pop("colors")
            slug = data.pop("slug")
            obj, _ = Category.objects.update_or_create(slug=slug, defaults=data)
            attach_image(obj, "image", f"{slug}.jpg", data["english_name"].upper(), colors, (500, 500))
        self.stdout.write("  ✓ دسته‌بندی محصولات")

    def seed_products(self, now):
        categories = {c.slug: c for c in Category.objects.all()}
        for data in PRODUCTS:
            data = dict(data)
            colors = data.pop("colors")
            days_ago = data.pop("days_ago")
            sku = data.pop("sku")
            data["category"] = categories[data.pop("category")]

            product, _ = Product.objects.update_or_create(sku=sku, defaults=data)
            # created_at با auto_now_add قابل تنظیم در save نیست؛ با update مقداردهی می‌شود
            Product.objects.filter(pk=product.pk).update(created_at=now - timedelta(days=days_ago))

            slug_name = sku.lower()
            attach_image(product, "image", f"{slug_name}.jpg", data["brand"], colors,
                         (800, 800), data["name_en"].split("•")[0].strip())

            if not product.images.exists():
                gallery = ProductImage(product=product, alt=f"{product.name} - نمای کناری", order=1)
                gallery.image.save(
                    f"{slug_name}-side.jpg",
                    make_image(f"{slug_name}-side.jpg", data["brand"], colors[::-1], (800, 800), "SIDE VIEW"),
                    save=True,
                )
        self.stdout.write("  ✓ محصولات و تصاویر گالری")

    def seed_blog(self, now):
        blog_categories = {}
        for slug, name, order in BLOG_CATEGORIES:
            blog_categories[slug], _ = BlogCategory.objects.update_or_create(
                slug=slug, defaults={"name": name, "order": order, "is_active": True}
            )

        tags = {}
        for slug, name in TAGS:
            tags[slug], _ = Tag.objects.update_or_create(slug=slug, defaults={"name": name})

        for data in POSTS:
            data = dict(data)
            colors = data.pop("colors")
            slug = data.pop("slug")
            post_tags = data.pop("tags")
            days_ago = data.pop("days_ago")

            post, _ = Post.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": data["title"],
                    "category": blog_categories[data["category"]],
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "status": Post.Status.PUBLISHED,
                    "is_featured": data["is_featured"],
                    "views_count": data["views"],
                    "published_at": now - timedelta(days=days_ago),
                },
            )
            post.tags.set([tags[t] for t in post_tags])
            attach_image(post, "image", f"{slug}.jpg", "VARIAN BLOG", colors, (1200, 700),
                         slug.replace("-", " ").upper())
        self.stdout.write("  ✓ بلاگ (دسته‌بندی، برچسب، مقاله)")

    def seed_hero(self):
        for data in HERO_SLIDES:
            data = dict(data)
            colors = data.pop("colors")
            label = data.pop("label")
            data["primary_btn_url"] = resolve_url(data["primary_btn_url"])
            slide, _ = HeroSlide.objects.update_or_create(
                title_line1=data.pop("title_line1"),
                title_highlight=data.pop("title_highlight"),
                defaults={**data, "is_active": True},
            )
            attach_image(slide, "image", f"hero-{slide.order}.jpg", label, colors, (800, 1000))
        self.stdout.write("  ✓ اسلایدهای هیرو")

    def seed_banners(self):
        for order, data in enumerate(BANNERS, start=1):
            data = dict(data)
            colors = data.pop("colors")
            label = data.pop("label")
            size = data.pop("size")
            data["button_url"] = resolve_url(data["button_url"])
            banner, _ = HomeBanner.objects.update_or_create(
                title=data.pop("title"),
                defaults={**data, "order": order, "is_active": True},
            )
            name = f"banner-{banner.placement}.jpg"
            attach_image(banner, "image", name, label, colors, size)
            if banner.placement == HomeBanner.Placement.BOTTOM:
                attach_image(banner, "mobile_image", f"banner-{banner.placement}-mobile.jpg",
                             label, colors, (700, 700))
        self.stdout.write("  ✓ بنرها (هر ۴ محل نمایش)")

    def seed_simple_models(self):
        for title, description, icon, order in STORE_FEATURES:
            StoreFeature.objects.update_or_create(
                title=title,
                defaults={"description": description, "icon": icon, "order": order, "is_active": True},
            )
        for title, value, suffix, icon, order in STATISTICS:
            HomeStatistic.objects.update_or_create(
                title=title,
                defaults={"value": value, "suffix": suffix, "icon": icon, "order": order, "is_active": True},
            )
        for order, (question, answer) in enumerate(FAQS, start=1):
            HomeFAQ.objects.update_or_create(
                question=question,
                defaults={"answer": answer, "order": order, "is_active": True},
            )
        self.stdout.write("  ✓ مزیت‌ها، آمار و سؤالات متداول")