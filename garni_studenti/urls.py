from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import botapp.bot
import parserapp.views

base = 'garni_studenti/'

urlpatterns = [
    path(base + 'admin/', admin.site.urls),
    path(base + 'parse/', parserapp.views.parse),
    path(base + 'bot/', botapp.bot.webhook_update),
] + static(base + settings.STATIC_URL, document_root=settings.STATIC_ROOT)
