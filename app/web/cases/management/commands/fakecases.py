from django.conf import settings
from django.core.management.base import BaseCommand
from faker import Faker
from web.cases.models import Case, CaseStatus


class Command(BaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        for i in range(200):
            f = Faker()
            c = Case()
            c.client_first_name = f.first_name()
            c.client_last_name = f.last_name()
            c.email = f.email()
            c.geboortedatum = f.date()
            c.save()

            s = CaseStatus()
            s.case = c
            s.status_comment = f"status number: {i}"
            s.save()