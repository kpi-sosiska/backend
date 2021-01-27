from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import botapp.bot
import parserapp.views
from garni_studenti.settings import BASE_URL


urlpatterns = [
    path(BASE_URL + 'admin/', admin.site.urls),
    path(BASE_URL + 'parse/', parserapp.views.parse),
    path(BASE_URL + 'bot/', botapp.bot.webhook_update),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
