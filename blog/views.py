from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Post, Tag


def published_posts():
    """مقالات منتشرشده در دسته‌بندی‌های فعال."""
    return (
        Post.objects.filter(status=Post.Status.PUBLISHED, category__is_active=True)
        .select_related("category", "author")
        .prefetch_related("tags")
    )


class PostListView(ListView):
    """لیست مقالات منتشرشده (+ فیلتر دسته / برچسب / جستجو / مرتب‌سازی)"""

    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 9

    SORT_OPTIONS = {
        "newest": ("جدیدترین", ("-published_at", "-created_at")),
        "oldest": ("قدیمی‌ترین", ("published_at", "created_at")),
        "views": ("پربازدیدترین", ("-views_count", "-published_at")),
        "title": ("بر اساس عنوان", ("title",)),
    }

    def get_queryset(self):
        qs = published_posts()

        # دسته‌بندی / برچسب از URL
        self.category = None
        self.tag = None
        if self.kwargs.get("category_slug"):
            self.category = get_object_or_404(
                Category, slug=self.kwargs["category_slug"], is_active=True
            )
            qs = qs.filter(category=self.category)
        if self.kwargs.get("tag_slug"):
            self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
            qs = qs.filter(tags=self.tag)

        # جستجو
        self.search_query = self.request.GET.get("q", "").strip()
        if self.search_query:
            qs = qs.filter(
                Q(title__icontains=self.search_query)
                | Q(excerpt__icontains=self.search_query)
                | Q(content__icontains=self.search_query)
            )

        # فقط ویژه
        self.only_featured = self.request.GET.get("featured") == "1"
        if self.only_featured:
            qs = qs.filter(is_featured=True)

        # مقالهٔ ویژهٔ بالای صفحه: فقط وقتی هیچ فیلتری فعال نیست.
        # از لیست حذف می‌شود تا تکراری دیده نشود (روی همهٔ صفحات، تا صفحه‌بندی جابه‌جا نشود).
        self.featured_post = None
        if not (self.category or self.tag or self.search_query or self.only_featured):
            self.featured_post = (
                qs.filter(is_featured=True).order_by("-published_at", "-created_at").first()
            )
            if self.featured_post:
                qs = qs.exclude(pk=self.featured_post.pk)

        # مرتب‌سازی
        self.sort = self.request.GET.get("sort", "newest")
        if self.sort not in self.SORT_OPTIONS:
            self.sort = "newest"
        return qs.order_by(*self.SORT_OPTIONS[self.sort][1]).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published_filter = Q(
            posts__status=Post.Status.PUBLISHED, posts__category__is_active=True
        )

        context["categories"] = (
            Category.objects.filter(is_active=True)
            .annotate(post_count=Count("posts", filter=published_filter))
            .order_by("order", "name")
        )
        context["tags"] = (
            Tag.objects.annotate(post_count=Count("posts", filter=published_filter))
            .filter(post_count__gt=0)
            .order_by("-post_count", "name")[:15]
        )
        context["total_posts"] = published_posts().count()
        context["current_category"] = self.category
        context["current_tag"] = self.tag
        context["search_query"] = self.search_query
        context["only_featured"] = self.only_featured
        context["current_sort"] = self.sort
        context["sort_options"] = [(key, label) for key, (label, _) in self.SORT_OPTIONS.items()]

        page_obj = context["page_obj"]
        context["featured_post"] = self.featured_post if page_obj.number == 1 else None
        context["page_range"] = context["paginator"].get_elided_page_range(
            page_obj.number, on_each_side=1, on_ends=1
        )
        context["is_filtered"] = bool(
            self.category or self.tag or self.search_query or self.only_featured
        )
        return context


class PostDetailView(DetailView):
    """صفحهٔ جزئیات مقاله"""

    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return published_posts()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # افزایش تعداد بازدید بدون race condition
        Post.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        obj.views_count += 1
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        others = published_posts().exclude(pk=post.pk)

        # مرتبط: همان دسته؛ اگر کم بود، با برچسب‌های مشترک تکمیل می‌شود
        related = list(others.filter(category=post.category).order_by("-published_at")[:3])
        if len(related) < 3:
            tag_ids = post.tags.values_list("id", flat=True)
            extra = (
                others.filter(tags__in=tag_ids)
                .exclude(pk__in=[p.pk for p in related])
                .distinct()
                .order_by("-published_at")[: 3 - len(related)]
            )
            related += list(extra)
        context["related_posts"] = related

        # مقالهٔ قبلی / بعدی بر اساس تاریخ انتشار
        if post.published_at:
            context["previous_post"] = (
                others.filter(published_at__lt=post.published_at).order_by("-published_at").first()
            )
            context["next_post"] = (
                others.filter(published_at__gt=post.published_at).order_by("published_at").first()
            )

        context["popular_posts"] = others.order_by("-views_count")[:4]
        context["categories"] = (
            Category.objects.filter(is_active=True)
            .annotate(
                post_count=Count(
                    "posts",
                    filter=Q(posts__status=Post.Status.PUBLISHED),
                )
            )
            .filter(post_count__gt=0)
            .order_by("order", "name")
        )
        return context