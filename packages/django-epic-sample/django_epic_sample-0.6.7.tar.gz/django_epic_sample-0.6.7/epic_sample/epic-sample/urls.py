from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    # Examples:
    # url(r'^$', 'tstproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^epic/', include(('epic.urls', 'epic'), namespace='epic'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
