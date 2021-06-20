import os

import django

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


async def gunicorn():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
    django.setup()

    from botapp.bot import get_webapp
    return get_webapp()
