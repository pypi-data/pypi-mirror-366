from django import http
from django.contrib import messages
from django.contrib.flatpages.views import render_flatpage
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from .models import Revision


@never_cache
def preview(request: http.HttpRequest, pk: int, key: str) -> http.HttpResponse:
    queryset = Revision.objects.select_related("page")
    revision = get_object_or_404(queryset, pk=pk, share_key=key)
    revision.publish(save=False, skip_check=True)
    warning_message = _("This is a preview page, do not share.")
    if request.user.has_perm("flatpages_extra.change_revision"):
        warning_message += format_html(
            ' <a href="{}">{}</a>',
            reverse("admin:flatpages_extra_revision_change", args=[revision.pk]),
            _("Edit it in the admin."),
        )
    messages.warning(request, mark_safe(warning_message))
    return render_flatpage(request, revision.page)
