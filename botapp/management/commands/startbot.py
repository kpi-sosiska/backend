import os

from aiogram.utils import executor
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start the bot'

    def handle(self, *args, **options):
        from botapp import dp, register
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

        register()
        executor.start_polling(dp)
