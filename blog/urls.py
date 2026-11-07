from django.urls import path

from .views import PostDetailView, PostListView

app_name = "blog"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    # <str:...> چون اسلاگ‌ها ممکن است فارسی باشند (converter «slug» فقط لاتین قبول می‌کند)
    path("category/<str:category_slug>/", PostListView.as_view(), name="post_list_by_category"),
    path("tag/<str:tag_slug>/", PostListView.as_view(), name="post_list_by_tag"),
    path("<str:slug>/", PostDetailView.as_view(), name="post_detail"),
]