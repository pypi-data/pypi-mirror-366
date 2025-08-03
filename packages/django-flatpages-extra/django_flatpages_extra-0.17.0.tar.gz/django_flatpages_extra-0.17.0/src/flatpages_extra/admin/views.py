from django.contrib import messages
from django.contrib.admin.helpers import AdminForm
from django.forms import Form
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import generic
from django.views.generic.detail import BaseDetailView

from .. import models
from . import forms


class BlankForm(Form):
    pass


class ModelAdminMixin:
    modeladmin = None
    admin_title = None
    admin_subtitle = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.modeladmin.admin_site.each_context(self.request))
        adminform = AdminForm(
            form=context.get("form", BlankForm()),
            fieldsets=[],
            prepopulated_fields={},
        )
        context.update(
            title=self.admin_title,
            subtitle=self.admin_subtitle,
            adminform=adminform,
            object_id=self.object.pk,
            original=self.object,
            is_popup=False,
            to_field=None,
            media=adminform.media,
            inline_admin_formsets=[],
            errors=None,
            preserved_filters=None,
        )
        # This will mutate the passed context, we can discard the return value:
        self.modeladmin.render_change_form(self.request, context, obj=self.object)
        return context


class FlatPageCreateRevisionView(generic.RedirectView):
    pattern_name = "admin:flatpages_extra_revision_add"

    def get_redirect_url(self, pk):
        url = super().get_redirect_url()
        return f"{url}?page={pk}"


class FlatPageContentAPIView(generic.View):
    def get(self, request):
        page = get_object_or_404(models.FlatPage, pk=request.GET.get("pk"))
        data = {"content": page.content}
        return JsonResponse(data)


class RevisionPreviewRedirectView(BaseDetailView):
    model = models.Revision

    def render_to_response(self, context):
        return redirect(context["object"])


class RevionsBaseActionView(ModelAdminMixin, generic.UpdateView):
    model = models.Revision
    success_message = None

    def get_success_message(self):
        return self.success_message

    def get_page_logentry_message(self):
        return self.object.description

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log a record for the page itself
        self.modeladmin.log_change(
            request=self.request,
            obj=self.object.page,
            message=self.get_page_logentry_message(),
        )
        # And log a record for the contrib.flatpages.FlatPage contenttype too
        self.modeladmin.log_change(
            request=self.request,
            obj=self.object.page.concrete_page,
            message=self.get_page_logentry_message(),
        )
        if success_message := self.get_success_message():
            messages.success(self.request, success_message)
        return response


class RevisionPublishView(RevionsBaseActionView):
    template_name = "admin/flatpages_extra/revision/publish.html"
    form_class = forms.RevisionPublishForm
    admin_title = "Publish revision"
    admin_subtitle = "Are you sure you want to publish this revision?"
    success_message = gettext_lazy(
        "The revision has been published. The new page should be live."
    )
    success_url = reverse_lazy("admin:flatpages_extra_revision_changelist")


class RevisionRevertView(RevionsBaseActionView):
    template_name = "admin/flatpages_extra/revision/revert.html"
    form_class = forms.RevisionRevertForm
    admin_title = "Revert revision"
    admin_subtitle = "Are you sure you want to revert this revision?"
    success_message = gettext_lazy(
        "The revision has been reverted. The old version should be live again."
    )
    success_url = reverse_lazy("admin:flatpages_extra_revision_changelist")

    def get_page_logentry_message(self):
        return f'Reverted "{self.object.description}"'


class RevisionCompareView(ModelAdminMixin, generic.DetailView):
    template_name = "admin/flatpages_extra/revision/compare.html"
    model = models.Revision
    admin_title = "Comparing revision with original"
