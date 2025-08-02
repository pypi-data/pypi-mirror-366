from django.core.management.base import BaseCommand

from share_links.models import Link
from share_links.utils import get_title


class Command(BaseCommand):
    help = "Loop on each saved link and check if the link is still available."

    def handle(self, *args, **options):
        nb = 0
        errors = []
        links = Link.objects.all()
        nb_links = len(links)
        for link in links:
            print(link.link, end="...\n")
            try:
                status = get_title(link.link)[0]
                status = "V"
                if status is True:  # online
                    errors.append(link)
                    link.online = False
                    status = "X"
            except Exception:
                errors.append(link)
                link.online = False
                status = "X"
            link.save()
            self.stdout.write(f"[{status}] [{str(nb + len(errors))}/{nb_links}]")
            nb += 1

        self.stdout.write("")
        self.stdout.write(self.style.ERROR(f"There was {str(len(errors))} errors:"))
        for error in errors:
            self.stdout.write(f"[{error.id}] {error.link}")
