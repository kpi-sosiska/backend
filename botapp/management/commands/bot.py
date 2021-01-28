from aiogram.utils import executor
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Bot control'

    def add_arguments(self, parser):
        parser.add_argument('--webhook', '-w', help='set webhook and die')

    def handle(self, *args, **options):
        from botapp.bot import dp, set_webhook

        if options['webhook']:
            set_webhook(options['webhook'])
        else:
            executor.start_polling(dp)
