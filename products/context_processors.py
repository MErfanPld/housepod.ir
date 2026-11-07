
from django.db.models import Prefetch
from .models import Category


def navbar_categories(request):
    categories = (
        Category.objects
        .filter(
            is_active=True,
            parent__isnull=True
        )
        .prefetch_related(
            Prefetch(
                "children",
                queryset=Category.objects.filter(
                    is_active=True
                ).order_by("order", "name"),
                to_attr="active_children"
            )
        )
        .order_by("order", "name")
    )

    return {
        "nav_categories": categories
    }
