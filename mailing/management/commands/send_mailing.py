from django.core.management.base import BaseCommand
from mailing.models import Mailing


class Command(BaseCommand):
    help = "Send mailing manually by its ID."

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", nargs="+", type=int)

    def handle(self, *args, **options):
        for mailing_id in options["mailing_id"]:
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
                mailing.send()  # Вызов метода отправки
                self.stdout.write(f"Successfully sent mailing {mailing_id}")
            except Mailing.DoesNotExist:
                self.stderr.write(f"Mailing #{mailing_id} does not exist.")
