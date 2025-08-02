from django.core.management.base import BaseCommand

from share_links.models import Link
from share_links.utils import get_lang


class Command(BaseCommand):
    help = "Loop on each saved link and try to add a language if it's not defined."

    def handle(self, *args, **options):
        nb = 0
        errors = []
        links = Link.objects.all()
        nb_links = len(links)
        for link in links:
            if link.allow_override_language:
                self.stdout.write(
                    f"[{str(nb + len(errors))}/{nb_links}] Adding language to {link.link} if missing..."
                )
                try:
                    status, text = get_lang(link.link)
                    if status is True:
                        self.stdout.write(
                            self.style.SUCCESS(f"  (New) language: {text}")
                        )
                        link.language = text
                        link.save()
                    else:
                        self.stdout.write(f"  Error: {text}.")
                        errors.append(link)
                    nb += 1
                    self.stdout.write("Done!")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))
                    errors.append(link)
            else:
                f"[{str(nb + len(errors))}/{nb_links}] Do not add language for {link.link} (allow_override_language is False)..."
                nb += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Added {nb} langs!"))

        self.stdout.write(self.style.ERROR(f"There was {str(len(errors))} errors:"))
        for error in errors:
            self.stdout.write(f"[{error.id}] {error.link}")
