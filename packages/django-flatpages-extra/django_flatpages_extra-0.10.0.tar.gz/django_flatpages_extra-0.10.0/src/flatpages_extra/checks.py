from django.apps import apps
from django.conf import settings
from django.core.checks import Error, register
from django.urls import NoReverseMatch

from . import models

E001_URLS_NOT_INSTALLED_ERROR = Error(
    "flatpages_extra URLs are not installed",
    hint=(
        'Add `path("flatpagesextra/", include("flatpages_extra.urls"))` '
        f"to your root urlconf ({settings.ROOT_URLCONF}).",
    ),
    id="flatpages_extra.E001",
)


E002_CONTRIB_FLATPAGES_NOT_INSTALLED_ERROR = Error(
    "contrib.flatpages is not installed",
    hint="Add 'contrib.flatpages' to settings.INSTALLED_APPS.",
    id="flatpages_extra.E002",
)


def check_urls_are_installed():
    revision = models.Revision(pk=123, share_key="asdf")
    try:
        revision.get_absolute_url()
    except NoReverseMatch:
        yield E001_URLS_NOT_INSTALLED_ERROR


def check_contrib_flatpages_is_installed():
    if not apps.is_installed("django.contrib.flatpages"):
        yield E002_CONTRIB_FLATPAGES_NOT_INSTALLED_ERROR


@register
def check_all(app_configs, **kwargs):
    errors = []
    errors.extend(check_urls_are_installed())
    errors.extend(check_contrib_flatpages_is_installed())

    return errors
