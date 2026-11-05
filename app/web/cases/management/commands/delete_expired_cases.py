import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.cases.services import delete_case_permanently, expired_delete_request_cases

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Verwijdert cliënten definitief waarvan het verwijderverzoek ouder is "
        "dan CASE_DELETE_SECONDS (standaard 30 dagen)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Toon alleen welke cliënten verwijderd zouden worden.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        cases = expired_delete_request_cases().order_by("delete_request_date")
        deleted, failed = 0, 0

        for case in cases.iterator():
            # Only log ids and dates, no personal data
            if dry_run:
                self.stdout.write(
                    "Zou verwijderen: case %s (verzoek %s)"
                    % (case.id, case.delete_request_date.isoformat())
                )
                deleted += 1
                continue
            case_id = case.id
            try:
                with transaction.atomic():
                    delete_case_permanently(case)
            except Exception:
                failed += 1
                logger.exception("Verwijderen van case %s mislukt", case_id)
                continue
            deleted += 1
            logger.info("Case %s automatisch definitief verwijderd", case_id)

        if dry_run:
            self.stdout.write("%s cliënt(en) zouden worden verwijderd" % deleted)
            return
        self.stdout.write("%s cliënt(en) verwijderd, %s mislukt" % (deleted, failed))
        if failed:
            # Non-zero exit so a failing CronJob is visible
            raise CommandError("%s cliënt(en) konden niet worden verwijderd" % failed)
