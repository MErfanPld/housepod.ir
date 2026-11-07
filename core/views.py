
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView

from .models import (
    HeroSlide,
    HomeBanner,
    StoreFeature,
    HomeStatistic,
    HomeFAQ,
)
from products.models import Category, Product
from blog.models import Post


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context["hero_slides"] = HeroSlide.objects.filter(
            is_active=True
        ).order_by("order")

        context["categories"] = Category.objects.filter(
            is_active=True,
            parent__isnull=True,
        ).order_by("order", "name")

        context["featured_products"] = (
            Product.objects.filter(
                is_active=True,
                is_featured=True,
                is_available=True,
                stock__gt=0,
                category__is_active=True,
            )
            .select_related("category")
            .prefetch_related("images")[:8]
        )

        context["latest_products"] = (
            Product.objects.filter(
                is_active=True,
                is_available=True,
                stock__gt=0,
                category__is_active=True,
            )
            .select_related("category")
            .prefetch_related("images")
            .order_by("-created_at")[:8]
        )

        context["home_banners"] = HomeBanner.objects.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        ).order_by("placement", "order")

        context["store_features"] = StoreFeature.objects.filter(
            is_active=True
        )

        context["home_statistics"] = HomeStatistic.objects.filter(
            is_active=True
        )

        context["home_faqs"] = HomeFAQ.objects.filter(
            is_active=True
        )

        context["latest_posts"] = (
            Post.objects.filter(
                status=Post.Status.PUBLISHED,
                category__is_active=True,
            )
            .select_related("category", "author")
            .order_by("-published_at", "-created_at")[:3]
        )

        return context
