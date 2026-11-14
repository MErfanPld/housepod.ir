from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Case, When, F, DecimalField
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode

from .models import Category, Product


class ProductListView(ListView):
    """لیست محصولات با فیلتر، جستجو، مرتب‌سازی و Pagination"""
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
        )

        # دسته‌بندی
        category_slug = self.kwargs.get("slug")
        if category_slug:
            self.category = get_object_or_404(
                Category, slug=category_slug, is_active=True
            )
            qs = qs.filter(category=self.category)
        else:
            self.category = None

        # جستجو
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(name_en__icontains=q)
                | Q(short_description__icontains=q)
                | Q(brand__icontains=q)
                | Q(flavor__icontains=q)
                | Q(sku__icontains=q)
            )

        # برند
        brand = self.request.GET.get("brand", "").strip()
        if brand:
            qs = qs.filter(brand__iexact=brand)

        # فقط موجود
        if self.request.GET.get("in_stock") == "1":
            qs = qs.filter(stock__gt=0, is_available=True)

        # محدوده قیمت (بر اساس قیمت نهایی)
        price_min = self.request.GET.get("price_min", "").strip()
        price_max = self.request.GET.get("price_max", "").strip()

        # محاسبه قیمت نهایی برای فیلتر و مرتب‌سازی
        # final_price = discount_price اگر وجود داشته و کمتر باشد، وگرنه price
        qs = qs.annotate(
            computed_final_price=Case(
                When(
                    discount_price__isnull=False,
                    discount_price__lt=F("price"),
                    then=F("discount_price"),
                ),
                default=F("price"),
                output_field=DecimalField(),
            )
        )

        if price_min.isdigit():
            qs = qs.filter(computed_final_price__gte=int(price_min))
        if price_max.isdigit():
            qs = qs.filter(computed_final_price__lte=int(price_max))

        # طعم (در صورت استفاده)
        flavor = self.request.GET.get("flavor")
        if flavor:
            qs = qs.filter(flavor__icontains=flavor)

        # سازگاری (در صورت استفاده)
        compatibility = self.request.GET.get("compatibility")
        if compatibility:
            qs = qs.filter(compatibility=compatibility)

        # مرتب‌سازی
        sort = self.request.GET.get("sort", "newest")
        if sort == "price_asc":
            qs = qs.order_by("computed_final_price")
        elif sort == "price_desc":
            qs = qs.order_by("-computed_final_price")
        elif sort == "name":
            qs = qs.order_by("name")
        elif sort == "featured":
            qs = qs.order_by("-is_featured", "-created_at")
        else:  # newest
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # دسته‌بندی‌ها با تعداد محصول
        context["categories"] = (
            Category.objects
            .filter(is_active=True)
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True)
                )
            )
            .order_by("order", "name")
        )
        context["current_category"] = getattr(self, "category", None)

        # مقادیر فعلی فیلترها
        search_query = self.request.GET.get("q", "").strip()
        current_brand = self.request.GET.get("brand", "").strip()
        in_stock = self.request.GET.get("in_stock", "")
        price_min = self.request.GET.get("price_min", "").strip()
        price_max = self.request.GET.get("price_max", "").strip()
        current_sort = self.request.GET.get("sort", "newest")

        context["search_query"] = search_query
        context["current_brand"] = current_brand
        context["in_stock"] = in_stock
        context["price_min"] = price_min
        context["price_max"] = price_max
        context["current_sort"] = current_sort
        context["compatibility_choices"] = Product.DeviceCompatibility.choices

        # لیست برندها (برای سایدبار)
        brand_qs = (
            Product.objects
            .filter(is_active=True)
            .exclude(brand="")
            .values("brand")
            .annotate(count=Count("id"))
            .order_by("brand")
        )
        if self.category:
            brand_qs = brand_qs.filter(category=self.category)
        context["brands"] = brand_qs

        # تعداد کل محصولات فعال (بدون فیلتر)
        context["total_active_products"] = Product.objects.filter(
            is_active=True
        ).count()

        # فیلترهای فعال برای نمایش
        active_filters = []
        if search_query:
            active_filters.append({"label": f"جستجو: {search_query}"})
        if current_brand:
            active_filters.append({"label": f"برند: {current_brand}"})
        if in_stock == "1":
            active_filters.append({"label": "فقط موجود"})
        if price_min:
            active_filters.append({"label": f"از {price_min} تومان"})
        if price_max:
            active_filters.append({"label": f"تا {price_max} تومان"})
        context["active_filters"] = active_filters

        # ساخت querystring برای Pagination (بدون page)
        params = self.request.GET.copy()
        if "page" in params:
            del params["page"]
        context["querystring"] = params.urlencode()

        return context


class ProductDetailView(DetailView):
    """صفحه جزئیات محصول"""
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        related = (
            Product.objects
            .filter(
                category=product.category,
                is_active=True,
            )
            .exclude(pk=product.pk)
            .select_related("category")
            [:4]
        )
        context["related_products"] = related
        context["categories"] = (
            Category.objects
            .filter(is_active=True)
            .order_by("order", "name")
        )
        return context