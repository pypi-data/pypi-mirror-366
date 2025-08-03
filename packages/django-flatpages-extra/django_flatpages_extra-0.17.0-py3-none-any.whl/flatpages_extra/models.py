import difflib
import typing
from collections import abc
from dataclasses import dataclass

from django.contrib.flatpages.models import FlatPage as OriginalFlatPage
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext, gettext_lazy
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DiffLexer

from . import exceptions

DiffType = abc.Iterable[str]


class FlatPage(OriginalFlatPage):
    class Meta:
        proxy = True

    @property
    def concrete_page(self):
        field_names = [f.name for f in self._meta.get_fields() if not f.is_relation]
        return OriginalFlatPage(**{f: getattr(self, f) for f in field_names})

    def make_initial_revision(self, published_on=None, save=True):
        if published_on is None:
            published_on = timezone.now()

        revision = Revision(
            page=self,
            content=self.content,
            previous_content="",
            description=gettext("Initial revision."),
            published_on=published_on,
        )
        if save:
            revision.save()
        return revision

    make_initial_revision.do_not_call_in_templates = True


def get_random_share_key() -> str:
    return get_random_string(10)


def get_content_field(**kwargs) -> models.Field:
    """
    Return a copy of the original flatpages' `content` field, with the given
    kwargs overridden.
    """
    original_field = OriginalFlatPage._meta.get_field("content")
    _, _, construct_args, construct_kwargs = original_field.deconstruct()
    construct_kwargs.update(kwargs)
    return original_field.__class__(*construct_args, **construct_kwargs)


@dataclass
class DiffStat:
    plus: int
    minus: int

    @classmethod
    def from_unified_diff(cls, diff: DiffType) -> typing.Self:
        # the first two lines are `---` and `+++` and I don't want them to be counted
        plus, minus = -1, -1
        for diffline in diff:
            if diffline.startswith("+"):
                plus += 1
            elif diffline.startswith("-"):
                minus += 1

        return cls(plus, minus)

    def __str__(self):
        return f"+{self.plus} / -{self.minus}"


class Revision(models.Model):
    class Status(models.IntegerChoices):
        UNPUBLISHED = 1
        PUBLISHED = 2
        REVERTED = 3

    # Local alias for exceptions for quicker access
    PublishError = exceptions.RevisionPublishError
    PublishStatusError = exceptions.RevisionPublishStatusError
    RevertError = exceptions.RevisionRevertError
    RevertStatusError = exceptions.RevisionRevertStatusError
    RevertContentError = exceptions.RevisionRevertContentError

    page = models.ForeignKey(FlatPage, on_delete=models.CASCADE, related_name="changes")
    content = get_content_field()
    previous_content = get_content_field(editable=False, blank=True)
    description = models.TextField(
        verbose_name=gettext_lazy("Description of the change"),
        help_text=gettext_lazy(
            "Describe the changes you've made. Future you will be thankful."
        ),
    )
    status = models.IntegerField(
        choices=Status, default=Status.UNPUBLISHED, editable=False
    )
    authors = models.ManyToManyField("auth.User", blank=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)
    published_on = models.DateTimeField(blank=True, null=True, editable=False)
    reverted_on = models.DateTimeField(blank=True, null=True, editable=False)
    share_key = models.CharField(
        max_length=10, default=get_random_share_key, editable=False
    )

    class Meta:
        ordering = ("-updated_on",)

    def __str__(self):
        return f"Revision #{self.pk}: {self.diffstats_text}"

    def get_absolute_url(self) -> str:
        from .views import preview  # avoid circular import

        return reverse(preview, kwargs={"pk": self.pk, "key": self.share_key})

    def raise_for_publish(self) -> None:
        if self.status != self.Status.UNPUBLISHED:
            raise self.PublishStatusError("Can only apply unpublished revisions")

    @property
    def can_publish(self) -> bool:
        try:
            self.raise_for_publish()
        except self.PublishError:
            return False
        else:
            return True

    def raise_for_revert(self) -> None:
        if self.status != self.Status.PUBLISHED:
            raise self.RevertStatusError("Can only revert published revisions")
        if self.page.content != self.content:
            raise self.RevertContentError(
                "Page has been modified since revision was published"
            )

    @property
    def can_revert(self) -> bool:
        try:
            self.raise_for_revert()
        except self.RevertError:
            return False
        else:
            return True

    def publish(self, save: bool = False, skip_check: bool = False) -> None:
        if not skip_check:
            self.raise_for_publish()

        self.previous_content = self.page.content
        self.page.content = self.content
        self.status = self.Status.PUBLISHED
        self.published_on = timezone.now()

        if save:
            with transaction.atomic():
                self.page.save(update_fields=["content"])
                self.save(update_fields=["status", "previous_content", "published_on"])

    def revert(self, save: bool = False, skip_check: bool = False) -> None:
        if not skip_check:
            self.raise_for_revert()

        self.page.content = self.previous_content
        self.status = self.Status.REVERTED
        self.reverted_on = timezone.now()
        if save:
            with transaction.atomic():
                self.page.save(update_fields=["content"])
                self.save(update_fields=["status", "reverted_on"])

    @property
    def original_content(self) -> str:
        if self.status == self.Status.UNPUBLISHED:
            return self.page.content
        else:
            return self.previous_content

    @property
    def unified_diff(self) -> DiffType:
        return difflib.unified_diff(
            self.original_content.splitlines(),
            self.content.splitlines(),
            lineterm="",
        )

    @property
    def highlighted_diff(self) -> SafeString:
        return mark_safe(
            highlight(
                "\n".join(self.unified_diff),
                DiffLexer(),
                HtmlFormatter(),
            )
        )

    @property
    def diffstats_text(self) -> str:
        return str(DiffStat.from_unified_diff(self.unified_diff))
