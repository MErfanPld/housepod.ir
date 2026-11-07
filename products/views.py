from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import Category, Product


class ProductListView(ListView):
    """لیست تمام محصولات فعال"""
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

        category_slug = self.kwargs.get("slug")
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug, is_active=True)
            qs = qs.filter(category=self.category)
        else:
            self.category = None

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(short_description__icontains=q)
                | Q(flavor__icontains=q)
                | Q(sku__icontains=q)
            )

        flavor = self.request.GET.get("flavor")
        if flavor:
            qs = qs.filter(flavor__icontains=flavor)

        compatibility = self.request.GET.get("compatibility")
        if compatibility:
            qs = qs.filter(compatibility=compatibility)

        if self.request.GET.get("in_stock") == "1":
            qs = qs.filter(stock__gt=0, is_available=True)

        sort = self.request.GET.get("sort", "newest")
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "name":
            qs = qs.order_by("name")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            Category.objects
            .filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
            .order_by("order", "name")
        )
        context["current_category"] = getattr(self, "category", None)
        context["search_query"] = self.request.GET.get("q", "")
        context["compatibility_choices"] = Product.DeviceCompatibility.choices
        return context


class ProductDetailView(DetailView):
    """صفحه جزئیات یک محصول"""
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
            .select_related("category")[:4]
        )
        context["related_products"] = related
        context["categories"] = Category.objects.filter(is_active=True).order_by("order", "name")
        return context
