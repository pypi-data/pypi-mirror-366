from django.conf import settings
from django.conf.global_settings import LANGUAGES as FULL_LANGUAGES_LIST
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_comments.moderation import CommentModerator, moderator
from parler.models import TranslatableModel, TranslatedFields, TranslationDoesNotExist

from share_links.apps.share_links_comments.models import CommentwithCaptcha
from share_links.conf import USE_WEASYPRINT


class Link(TranslatableModel):
    link = models.CharField(_("Link"), max_length=2000, unique=True)
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=2000, null=True, blank=True),
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_("You can use markdown here."),
        ),
    )
    tags = models.ManyToManyField(to="Tag", related_name="links", blank=True)
    highlight = models.BooleanField(
        default=False,
        blank=True,
        help_text=_(
            'Link will be displayed with a special color, and will appear in the "highlighted" sort option.'
        ),
    )
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.FileField(
        upload_to="files/",
        null=True,
        blank=True,
        help_text=_(
            f"Upload pdf or screenshot of the page. If this field is empty and USE_WEASYPRINT is set to True (currently set to {USE_WEASYPRINT}), then the pdf will be auto-generated using weasyprint."
        ),
    )
    save_file = models.BooleanField(
        default=True,
        help_text=_(
            "Uncheck this box if you don't want the file to be auto-generated."
        ),
    )
    online = models.BooleanField(
        default=True,
        help_text=_(
            "Uncheck this box if the link is not online anymore (will provide the web archive link instead of the original link)."
        ),
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    language = models.CharField(
        verbose_name=_("Language"),
        choices=FULL_LANGUAGES_LIST,
        max_length=7,
        null=True,
        blank=True,
    )
    allow_override_title = models.BooleanField(
        verbose_name=_("Allow override title?"),
        help_text=_(
            "Management commands will try to fetch the title from the website &lt;title&gt; tag."
        ),
        default=False,
    )
    allow_override_language = models.BooleanField(
        verbose_name=_("Allow override language?"),
        help_text=_(
            "Management commands will try to fetch the language from the lang attribute."
        ),
        default=False,
    )
    comments = GenericRelation(to=CommentwithCaptcha, object_id_field="object_pk")

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        try:
            return f"{self.title} ({self.link})"
        except TranslationDoesNotExist:
            return f"{self.link}"

    def get_absolute_url(self):
        return reverse("link", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if USE_WEASYPRINT and not self.file and self.save_file:
            from re import compile

            from django.core.files.base import ContentFile
            from weasyprint import HTML

            url_format = compile(r"https?://(www\.)?")
            file_name = (
                url_format.sub("", self.link).strip().strip("/").replace("/", "_")
                + ".pdf"  # noqa
            )
            try:
                pdf = HTML(self.link).write_pdf()
                pdf = ContentFile(pdf)

                self.file.save(file_name, pdf, save=False)
            except Exception:  # so much random errors! ignore them for now
                pass

        super().save(*args, **kwargs)


class EntryModerator(CommentModerator):
    email_notification = False


moderator.register(Link, EntryModerator)


class Category(TranslatableModel):
    translations = TranslatedFields(
        label=models.CharField(_("Label"), max_length=2048),
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_("You can use markdown here."),
        ),
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.label


class Tag(TranslatableModel):
    translations = TranslatedFields(
        tag=models.CharField(_("Tag"), max_length=2000),
        slug=models.SlugField(_("Slug"), max_length=2000, allow_unicode=True),
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_("You can use markdown here."),
        ),
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tags",
    )
    highlight = models.BooleanField(
        default=False,
        blank=True,
        help_text=_(
            'Tag will be displayed with a special color, and will appear in the "highlighted" sort option.'
        ),
    )
    date_added = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return f"{self.tag}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super().save(*args, **kwargs)


@receiver(pre_save, sender=Tag)
def pre_save_for_categories_and_tags_fixture(sender, instance, **kwargs):
    if kwargs["raw"]:
        instance.date_added = timezone.now()


class AboutContactPages(TranslatableModel):
    translations = TranslatedFields(
        page_title=models.CharField(_("Title"), max_length=255, blank=True, null=True),
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_("You can use markdown here."),
        ),
    )

    def __str__(self):
        return f"{str(self.id)} − {self.page_title}"

    class Meta:
        verbose_name = _("About & Contact Pages")
        verbose_name_plural = _("About & Contact Pages")


class Collection(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            _("Name"),
            max_length=1024,
            help_text=_("The name of the collection."),
        ),
        slug=models.SlugField(_("Slug"), max_length=2000, editable=False, unique=True),
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_("You can use markdown here."),
        ),
    )
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    highlight = models.BooleanField(
        default=False,
        blank=True,
        help_text=_(
            'Collection will be displayed with a special color, and will appear in the "highlighted" sort option.'
        ),
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CollectionLink(TranslatableModel):
    translations = TranslatedFields(
        description=models.TextField(
            _("Description"),
            blank=True,
            null=True,
            help_text=_(
                "You can use markdown here. If the description is empty, the link description will be used (if it exists)."
            ),
        )
    )
    link = models.ForeignKey("Link", on_delete=models.CASCADE)
    collection = models.ForeignKey("Collection", on_delete=models.CASCADE)

    def __str__(self):
        if self.link.title:
            return self.link.title
        return self.link.link
