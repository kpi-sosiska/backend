from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

import pics.views
from mainapp.api import router

urlpatterns = [
    path('admin/', admin.site.urls),
    url('pic/', pics.views.main),
    path('api/', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
