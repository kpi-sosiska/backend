from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from garni_studenti.settings import BASE_URL


urlpatterns = [
    path(BASE_URL + 'admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
