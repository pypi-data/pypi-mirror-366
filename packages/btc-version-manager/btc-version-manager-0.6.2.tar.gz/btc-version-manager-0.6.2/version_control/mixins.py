from django import forms
from django.contrib.auth.mixins import AccessMixin
from django.views import View


class AdminSiteViewMixin(AccessMixin):
    """
    A mixin that checks administrator rights or staff
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated or user.is_authenticated and (not user.is_staff or not user.is_superuser):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminSiteView(AdminSiteViewMixin, View):
    """
    A simple base view for admin site views
    """

    pass


class VersionControlFormMixin:
    """
    History handler form mixin

    Skipping history recording in the model and history recording after saving m2m relation in form
    """

    def save(self, commit=True):
        setattr(self.instance, "skip_handle_version", True)
        return super().save(commit)

    def _save_m2m(self):
        super()._save_m2m()
        try:
            if self.has_changed():
                self.instance.handle_version()
                delattr(self.instance, "skip_handle_version")
        except AttributeError:
            pass


class VersionControlModelForm(VersionControlFormMixin, forms.ModelForm):
    """
    History handler model form
    """

    pass


class VersionControlModelAdminMixin:
    """
    History handler model admin mixin
    """

    form = VersionControlModelForm
