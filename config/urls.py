
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('order/', include('order.urls')),

    path('blogs/', include('blog.urls')),

    path('products/', include('products.urls')),

path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),

    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml',
        content_type='application/xml'
    )),
    
path('googled755fb96396c7153.html', TemplateView.as_view(
    template_name='googled755fb96396c7153.html',
    content_type='text/html'
)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
