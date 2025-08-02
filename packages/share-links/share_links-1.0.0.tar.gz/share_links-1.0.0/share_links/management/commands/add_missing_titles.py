from django.conf import settings
from django.core.management.base import BaseCommand

from share_links.models import Link
from share_links.utils import get_title

languages_list = settings.LANGUAGES


class Command(BaseCommand):
    help = "Loop on each saved link and add a title if it's not defined."

    def handle(self, *args, **options):
        nb = 0
        errors = []
        links = Link.objects.all()
        nb_links = len(links)
        for link in links:
            if link.allow_override_title:
                self.stdout.write(
                    f"[{str(nb + len(errors))}/{nb_links}] Adding title to {link.link} if missing..."
                )
                try:
                    title = get_title(link.link)
                    for language in languages_list:
                        self.stdout.write(f"Doing {language[0]}... ")
                        link.set_current_language(language[0])
                        try:
                            if link.title is None or link.title == "":
                                self.stdout.write(
                                    self.style.SUCCESS(f"  New title: {title}")
                                )
                                link.title = title
                                link.save()
                            else:
                                self.stdout.write(f"  No new title: '{link.title}'")
                        except link.DoesNotExist:
                            self.stdout.write(f"  New title: {title}")
                            link.title = title
                            link.save()
                    nb += 1
                    self.stdout.write("Done!")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error: {e}"))
                    errors.append(link)
            else:
                f"[{str(nb + len(errors))}/{nb_links}] Do not update title for {link.link} (allow_override_title is False)..."
                nb += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Added {nb} titles!"))

        self.stdout.write(self.style.ERROR(f"There was {str(len(errors))} errors:"))
        for error in errors:
            self.stdout.write(f"[{error.id}] {error.link}")
