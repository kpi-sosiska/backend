from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import parserapp.views

urlpatterns = [
    path('/', admin.site.urls),
    path('parse/', parserapp.views.parse)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
