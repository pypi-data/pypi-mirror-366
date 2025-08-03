from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget, AutocompleteSelect
from django.contrib.flatpages.forms import FlatpageForm as OriginalFlatpageForm
from django.urls import reverse

from .. import models


class ContentWidget(AdminTextareaWidget):
    template_name = "admin/flatpages_extra/flatpage/widgets/content.html"

    def __init__(self, *args, page_pk=None, **kwargs):
        self.page_pk = page_pk
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["page_pk"] = self.page_pk
        return context


class FlatpageForm(OriginalFlatpageForm):
    class Meta:
        model = models.FlatPage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance._state.adding:
            self.fields["content"].widget = ContentWidget(page_pk=self.instance.pk)


class PageForeignKeyWidget(AutocompleteSelect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update(
            {
                "data-fpe-contentapi-url": reverse(
                    "admin:flatpages_extra_flatpage_contentapi"
                )
            }
        )

    @property
    def media(self):
        custom_js = [
            "admin/js/jquery.init.js",
            "admin/flatpages_extra/page-fk-widget.js",
        ]
        return super().media + forms.Media(js=custom_js)


class RevisionForm(forms.ModelForm):
    def __init__(self, *args, request, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        if pagepk := self.initial.get("page"):
            # For some reason the js triggers anyway, so this might not be necessary
            self.instance.page = models.FlatPage.objects.get(pk=pagepk)
            self.initial.update(
                content=self.instance.page.content,
            )

    def _save_m2m(self):
        super()._save_m2m()
        self.instance.authors.add(self.request.user)

    class Meta:
        widgets = {
            "description": forms.TextInput(attrs={"class": "vLargeTextField"}),
        }


class RevisionBaseActionForm(forms.ModelForm):
    method_name = None

    class Meta:
        model = models.Revision
        fields = []

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError
        getattr(self.instance, self.method_name)(save=True)
        return self.instance


class RevisionPublishForm(RevisionBaseActionForm):
    method_name = "publish"


class RevisionRevertForm(RevisionBaseActionForm):
    method_name = "revert"
