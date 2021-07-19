from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import mainapp.views
import pics.views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('pic/', pics.views.main),
    url('test/', mainapp.views.main),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
