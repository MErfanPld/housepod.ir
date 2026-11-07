from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """دستهبندی مقالات بلاگ"""

    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="نام دستهبندی",
    )
    slug = models.SlugField(
        max_length=140,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
        help_text="برای استفاده در URL (به صورت خودکار از نام ساخته میشود)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "دستهبندی بلاگ"
        verbose_name_plural = "دستهبندیهای بلاگ"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_list_by_category", kwargs={"category_slug": self.slug})


class Tag(models.Model):
    """برچسب مقالات"""

    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="نام برچسب",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسبها"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_list_by_tag", kwargs={"tag_slug": self.slug})


class Post(models.Model):
    """مقاله / پست بلاگ"""

    class Status(models.TextChoices):
        DRAFT = "draft", "پیشنویس"
        PUBLISHED = "published", "منتشر شده"

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=270,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
        help_text="برای استفاده در URL",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="دستهبندی",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="برچسبها",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
        verbose_name="نویسنده",
    )
    excerpt = models.CharField(
        max_length=400,
        blank=True,
        verbose_name="خلاصه / چکیده",
        help_text="متن کوتاه برای نمایش در لیست مقالات",
    )
    content = models.TextField(
        verbose_name="محتوای کامل",
    )
    image = models.ImageField(
        upload_to="blog/",
        blank=True,
        null=True,
        verbose_name="تصویر شاخص",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="مقاله ویژه",
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد بازدید",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ انتشار",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            self.slug = base_slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED