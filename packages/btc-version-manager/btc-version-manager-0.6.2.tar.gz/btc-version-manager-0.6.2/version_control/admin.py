from django.contrib import admin

from version_control.collections import ModelObjectChangeApp, ModelObjectChangeType
from version_control.helpers import VersionManagerDiffChecker
from version_control.models import ModelObjectVersion, ModelObjectVersionGroup


class ChangeTypeListFilter(admin.SimpleListFilter):
    """
    A custom filter for filtering objects by "change_type" field.
    """

    title = "Тип изменения"
    parameter_name = "change_type"

    def lookups(self, request, model_admin):
        # lookup for create/update/delete choices only
        return ModelObjectChangeType.CRUD_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(change_type=value)


class ChangeAppListFilter(admin.SimpleListFilter):
    """
    A custom filter for filtering objects by "app_name" field.
    """

    title = "App изменения"
    parameter_name = "change_app"

    def lookups(self, request, model_admin):
        # lookup for admin/not admin apps
        return ModelObjectChangeApp.CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(change_app=value)


class ContentTypeListFilter(admin.SimpleListFilter):
    """
    A custom filter for filtering objects by "content_type".
    """

    title = "Тип объекта"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        # lookup for currently tracked content types
        return ModelObjectVersionGroup.get_content_type_choices_for_vcs_objects()

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(content_type__pk=value)


class ModelObjectVersionAdmin(admin.ModelAdmin):
    """
    'ModelObjectVersion' model admin handler.
    Passes the necessary context variables for version comparison.
    """

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        version = ModelObjectVersion.objects.filter(id=object_id).first()
        previous_version = version.get_previous_version()
        next_version = version.get_next_version()
        template_processor = VersionManagerDiffChecker([previous_version, version])
        extra_context.update(
            dict(
                previous_version=previous_version,
                next_version=next_version,
                template_processor=template_processor,
            )
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class ModelObjectVersionGroupAdmin(admin.ModelAdmin):
    """
    'ModelObjectVersionGroup' model admin handler.
    Redirects to the version group change-view by version group ID or version group content object parameters:
    [content object app label]/[content object content type model name]/[content object id].
    """

    def change_view(self, request, object_id, form_url="", extra_context=None):
        filter_args = str(object_id).split("/")
        # check for object_id components
        if len(filter_args) == 3:
            # lookup for existing version groups and extract real version group ID
            vcs_group = ModelObjectVersionGroup.objects.filter(
                content_type__app_label=filter_args[0],
                content_type__model=filter_args[1],
                object_id=filter_args[2],
            ).first()
            if vcs_group:
                object_id = str(vcs_group.id)

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
