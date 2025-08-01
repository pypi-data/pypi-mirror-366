from django.db.models import QuerySet

from version_control.helpers import VersionWrapper


def decorate_queryset_method(queryset_func):
    """
    A decorator function for extending queryset class methods
    """

    def queryset_method(self, *args, **kwargs):
        # check for object model class
        first_obj = self._chain()[:1]
        first_obj = first_obj[0] if first_obj else None
        if (
            first_obj is not None
            and getattr(first_obj.__class__, "VERSION_MANAGER_ENABLED", False)
            and getattr(first_obj.__class__, "WRITE_CHANGES", False)
        ):
            # get old and updated querysets
            old_states = list(self._chain())
            output = queryset_func(self, *args, **kwargs)
            current_states = list(self._chain())

            # sort for comparison
            old_states.sort(key=lambda x: x.id)
            current_states.sort(key=lambda x: x.id)

            # lookup for changes
            chain_to_process = set(
                [
                    obj
                    for index, obj in enumerate(current_states)
                    if VersionWrapper(obj) != VersionWrapper(old_states[index])
                ]
            )

            # write versions for changed objects
            for obj in chain_to_process:
                obj.handle_version()
        else:
            output = queryset_func(self, *args, **kwargs)
        return output

    return queryset_method


class VersionManagerQuerysetManagerMethods:
    """
    A class with necessary overridden QuerySetManager's methods
    """

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        bulk_created_objects = super().bulk_create(objs, batch_size, ignore_conflicts)
        first_obj = bulk_created_objects[:1]
        first_obj = first_obj[0] if first_obj else None
        if (
            getattr(first_obj, "pk", False)
            and getattr(first_obj.__class__, "VERSION_MANAGER_ENABLED", False)
            and getattr(first_obj.__class__, "WRITE_CREATION", False)
        ):
            for obj in bulk_created_objects:
                obj.handle_version()
        return bulk_created_objects


class VersionControlModelManagerMixin(VersionManagerQuerysetManagerMethods):
    """
    A queryset manager for tracking model objects versions after QuerySet manager's bulk_create/update/delete
    operations.
    """

    def _extend_queryset_methods(self, methods: list) -> None:
        if not hasattr(self._queryset_class, "decorated_by_version_manager"):
            # prevent multiply decorating
            setattr(self._queryset_class, "decorated_by_version_manager", True)
            for method in methods:
                method_object = getattr(self._queryset_class, method, None)
                if method_object:
                    setattr(
                        self._queryset_class,
                        method,
                        decorate_queryset_method(method_object),
                    )


class ModelObjectVersionGroupQuerySet(QuerySet):
    """
    A queryset-manager for "ModelObjectVersionGroup" model
    """

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).prefetch_related("model_object_versions")


class ModelObjectVersionQuerySet(QuerySet):
    """
    A queryset-manager for "ModelObjectVersion" model
    """

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).select_related("group")
