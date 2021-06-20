from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Bot control'

    def add_arguments(self, parser):
        parser.add_argument('--webhook', '-w', help='start webhook')

    def handle(self, *args, **options):
        from botapp.bot import start_polling, start_webhook

        if options['webhook']:
            start_webhook()
        else:
            start_polling()
