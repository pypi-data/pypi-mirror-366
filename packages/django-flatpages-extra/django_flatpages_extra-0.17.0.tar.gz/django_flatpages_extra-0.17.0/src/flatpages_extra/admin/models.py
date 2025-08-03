import dataclasses
import typing
from functools import partial

from django import http
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin as OriginalFlatPageAdmin
from django.contrib.flatpages.models import FlatPage as OriginalFlatPage
from django.db.models import Model
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy
from django.views import View

from .. import models
from . import forms, views


class UnBoundRowActionException(Exception):
    pass


@dataclasses.dataclass
class RowAction:
    slug: str
    text: str
    url_name: str
    instance: Model | None = None

    def bind(self, instance: Model) -> typing.Self:
        return dataclasses.replace(self, instance=instance)

    @property
    def is_bound(self) -> bool:
        return self.instance is not None

    @property
    def url(self):
        if not self.is_bound:
            raise UnBoundRowActionException("RowAction must be bound")
        return reverse(self.url_name, args=[self.instance.pk])

    def as_html(self) -> SafeString:
        return format_html(
            '<li class="row-action"><a class="button fpe-action fpe-action-{slug}" href="{url}">{text}</a></li>',
            slug=self.slug,
            url=self.url,
            text=self.text,
        )


class ActionButtonColumnMixin:
    """
    Automatically add a column with action buttons
    """

    row_action_list: list[RowAction] = []

    def get_list_display(self, request: http.HttpRequest) -> list[str]:
        # Add `action_buttons` to `list_display` if it's not in there yet
        list_display = super().get_list_display(request)
        if "row_actions_column" not in list_display:
            list_display = [*list_display, "row_actions_column"]
        return list_display

    def get_row_action_list(self, obj: Model) -> list[RowAction]:
        actions = []
        for action in self.row_action_list:
            actions.append(action.bind(obj))
        return actions

    @admin.display(description=gettext_lazy("Actions"))
    def row_actions_column(self, obj) -> SafeString | None:
        actions = self.get_row_action_list(obj)
        if not actions:
            return None

        items = "\n".join(action.as_html() for action in actions)
        return mark_safe(f"<ul>\n{items}\n</ul>")


class AdminCBVMixin:
    def admin_cbv(self, view_class: View, **view_init_kwargs):
        if issubclass(view_class, views.ModelAdminMixin):
            view_init_kwargs["modeladmin"] = self

        return self.admin_site.admin_view(view_class.as_view(**view_init_kwargs))


admin.site.unregister(OriginalFlatPage)


@admin.register(models.FlatPage)
class FlatPageAdmin(ActionButtonColumnMixin, AdminCBVMixin, OriginalFlatPageAdmin):
    form = forms.FlatpageForm
    row_action_list = [
        RowAction(
            "addrevision",
            gettext_lazy("Add revision"),
            "admin:flatpages_extra_flatpage_addrevision",
        ),
    ]

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name

        return [
            path(
                "<int:pk>/add-revision/",
                self.admin_cbv(views.FlatPageCreateRevisionView),
                name="%s_%s_addrevision" % info,
            ),
            path(
                "_content_api/",
                self.admin_cbv(views.FlatPageContentAPIView),
                name="%s_%s_contentapi" % info,
            ),
            *super().get_urls(),
        ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            obj.make_initial_revision(save=True)


@admin.register(models.Revision)
class RevisionAdmin(ActionButtonColumnMixin, AdminCBVMixin, admin.ModelAdmin):
    form = forms.RevisionForm
    list_display = [
        "page",
        "description",
        "diffstats",
        "status",
    ]
    list_filter = ["status"]
    date_hierarchy = "created_on"
    row_action_list = [
        RowAction(
            "publish", gettext_lazy("Publish"), "admin:flatpages_extra_revision_publish"
        ),
        RowAction(
            "revert", gettext_lazy("Revert"), "admin:flatpages_extra_revision_revert"
        ),
        RowAction(
            "preview", gettext_lazy("Preview"), "admin:flatpages_extra_revision_preview"
        ),
        RowAction(
            "compare", gettext_lazy("Compare"), "admin:flatpages_extra_revision_diff"
        ),
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "page":
            kwargs["widget"] = forms.PageForeignKeyWidget(db_field, self.admin_site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name

        return [
            path(
                "<int:pk>/preview/",
                self.admin_cbv(views.RevisionPreviewRedirectView),
                name="%s_%s_preview" % info,
            ),
            path(
                "<int:pk>/diff/",
                self.admin_cbv(views.RevisionCompareView),
                name="%s_%s_diff" % info,
            ),
            path(
                "<int:pk>/publish/",
                self.admin_cbv(views.RevisionPublishView),
                name="%s_%s_publish" % info,
            ),
            path(
                "<int:pk>/revert/",
                self.admin_cbv(views.RevisionRevertView),
                name="%s_%s_revert" % info,
            ),
            *super().get_urls(),
        ]

    def get_row_action_list(self, obj):
        actions = []
        for action in super().get_row_action_list(obj):
            if (
                action.slug == "preview"
                and obj.status != models.Revision.Status.UNPUBLISHED
            ):
                continue
            if (
                action.slug == "publish"
                and obj.status != models.Revision.Status.UNPUBLISHED
            ):
                continue
            if (
                action.slug == "revert"
                and obj.status != models.Revision.Status.PUBLISHED
            ):
                continue
            if action.slug == "revert" and obj.previous_content == "":
                continue
            actions.append(action)
        return actions

    def get_form(self, request, obj=None, change=False, **kwargs):
        original_form_class = super().get_form(request, obj, change, **kwargs)

        form_class = partial(original_form_class, request=request)
        # Using a partial _almost_ works, but something somewhere later down the
        # line is introspecting the class's `base_fields`, so copy that too.
        form_class.base_fields = original_form_class.base_fields
        return form_class

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is not None:
            fields.remove("page")
        return fields

    @admin.display(description="Lines changed")
    def diffstats(self, revision):
        return revision.diffstats_text
