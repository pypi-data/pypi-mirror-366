import json
from typing import Optional, Type

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.cache import cache
from django.db import models
from django.db.models import JSONField
from django.db.models.base import ModelBase
from django.utils.timezone import now as tz_now

from version_control.collections import ModelObjectChangeType
from version_control.debugger import get_version_manager_debugger_class
from version_control.helpers import VersionProxy, VersionProxyField
from version_control.managers import (
    ModelObjectVersionGroupQuerySet,
    ModelObjectVersionQuerySet,
    VersionControlModelManagerMixin,
)
from version_control.utils import build_vcs_relation_tree, format_date, get_class_from_settings, get_str_hash


def get_version_manager_abstract_model_class() -> Type["BaseAbstractVersionControl"]:
    """
    Returns current version manager abstract model class from the project settings or original "AbstractVersionControl"
    """

    error_message = (
        'Не найден указанный в "settings" абстрактный класс модели менеджера версий. '
        'Используется стандартный - "AbstractVersionControl"'
    )
    return get_class_from_settings("VERSION_MANAGER_ABSTRACT_MODEL_CLASS", error_message, AbstractVersionControl)


class ModelObjectVersionGroup(models.Model):
    """
    The model for binding versions of model objects (version group)
    """

    representation = models.TextField(verbose_name="Описание объекта")
    verbose_name = models.TextField(verbose_name="Наименование объекта")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    relation_tree = JSONField(verbose_name="Дерево отношений", null=True)
    tree_last_update = models.DateTimeField(verbose_name="Последнее обновление дерева отношений", null=True)

    objects = ModelObjectVersionGroupQuerySet.as_manager()

    class Meta:
        verbose_name = "Группа версий объекта"
        verbose_name_plural = "Группы версий объектов"
        unique_together = (("content_type", "object_id"),)

    def __str__(self):
        return f"Группа версий объекта: {self.representation}"

    @classmethod
    def get_content_type_choices_for_vcs_objects(cls, cache_timeout: int = 120) -> tuple:
        from version_control.service import get_version_manager_class

        def get_choices() -> tuple:
            manager_class = get_version_manager_class()
            model_classes = manager_class().get_version_control_model_classes(to_str=True)
            return tuple(
                (content_type.pk, content_type) for content_type in ContentType.objects.filter(model__in=model_classes)
            )

        return cache.get_or_set("vcs_content_type_choices", default=get_choices, timeout=cache_timeout)

    def update_vcs_relation_tree(self) -> None:
        if self.content_object:
            vcs_tree, vcs_missed_objects_tree = build_vcs_relation_tree(self.content_object)
            self.relation_tree = dict(
                vcs_relation_tree=vcs_tree,
                vcs_missed_objects_relation_tree=vcs_missed_objects_tree,
            )
            self.tree_last_update = tz_now()
            self.save()

    def get_vcs_relation_tree(self) -> Optional[list]:
        data = None
        if self.relation_tree:
            data = self.relation_tree.get("vcs_relation_tree")
        return data

    def get_vcs_missed_objects_relation_tree(self) -> Optional[list]:
        data = None
        if self.relation_tree:
            data = self.relation_tree.get("vcs_missed_objects_relation_tree")
        return data


class ModelObjectVersion(models.Model):
    """
    The model for storing versions of model objects
    """

    group = models.ForeignKey(
        ModelObjectVersionGroup,
        related_name="model_object_versions",
        verbose_name="Группа версий",
        on_delete=models.CASCADE,
    )
    change_type = models.CharField(
        verbose_name="Тип изменения объекта",
        max_length=50,
        choices=ModelObjectChangeType.CHOICES,
        default=ModelObjectChangeType.OBJECT_CHANGED,
    )
    change_url = models.TextField(verbose_name="URL создания версии", null=True)
    change_app = models.TextField(verbose_name="APP создания версии", null=True)
    created = models.DateTimeField(verbose_name="Дата и время версии")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        related_name="model_objects_versions",
        on_delete=models.SET_NULL,
        null=True,
    )
    request_key = models.UUIDField(verbose_name="Уникальный ключ request", null=True)
    hash = models.UUIDField(verbose_name="Хэш версии")
    state = JSONField(null=True)

    objects = ModelObjectVersionQuerySet.as_manager()

    class Meta:
        verbose_name = "Версия объекта"
        verbose_name_plural = "Версии объектов"
        ordering = ("-created",)

    def __str__(self):
        return f'Версия объекта ({self.hash}) "{self.group.representation}": {format_date(self.created, "d.m.Y H:i")}'

    def get_state(self) -> dict:
        # state may be a string or a dictionary
        loaded_state = json.loads(self.state) if isinstance(self.state, str) else self.state
        return loaded_state[0] if isinstance(loaded_state, list) else loaded_state or {}

    def get_fields(self) -> list:
        # get all fields of the changed object
        fields = []
        model_class = self.group.content_type.model_class()
        if model_class:
            fields = [field.name for field in model_class._meta.local_fields]
        return fields

    def get_version_proxy(self) -> VersionProxy:
        # get and prepare all fields changes
        state = self.get_state()
        fields_extra_data = state.get("fields_extra_data", {})
        version_proxy = VersionProxy(version=self, fields={})
        if state:
            for name, value in state["fields"].items():
                version_proxy.fields[name] = VersionProxyField(name, value, fields_extra_data.get(name, {}))
        return version_proxy

    def is_deleted(self) -> bool:
        return self.change_type == ModelObjectChangeType.OBJECT_DELETED

    @property
    def proxy_object(self) -> models.Model:
        # get the deserialized version state object
        proxy_object = None
        deserialized_state = self.get_state_deserialized()
        if deserialized_state:
            _, proxy_object = deserialized_state
        return proxy_object

    def get_previous_version(self) -> "ModelObjectVersion":
        return ModelObjectVersion.objects.filter(group=self.group, id__lt=self.id).order_by("-created").first()

    def get_next_version(self) -> "ModelObjectVersion":
        return ModelObjectVersion.objects.filter(group=self.group, id__gt=self.id).order_by("created").first()

    def is_last_version(self) -> bool:
        return not ModelObjectVersion.objects.filter(group=self.group, id__gt=self.id).exists()

    def get_state_deserialized(self) -> tuple:
        # deserialize the state of a model object stored in version
        deserialized_object, proxy_object = None, None
        if self.state:
            wrapper_generator = serializers.deserialize("json", self.state, ignorenonexistent=True)
            for item in wrapper_generator:
                deserialized_object, proxy_object = item, item.object
                break
        return deserialized_object, proxy_object


class VersionManagerMeta(ModelBase):
    """
    The Meta class for adding custom logic for model's queryset managers by extending their base class sets with
    "VersionControlQuerysetManager".
    The "VersionControlQuerysetManager" class provides tracking for queryset managers's "bulk_create", "update",
    "delete" operations.
    """

    def __new__(mcs, name, bases, attrs):
        new = super().__new__(mcs, name, bases, attrs)
        for manager in new._meta.managers:
            manager_cls = manager.__class__
            manager.__class__ = type(
                manager_cls.__name__,
                (VersionControlModelManagerMixin, *manager_cls.__bases__),
                dict(manager_cls.__dict__),
            )
            manager._extend_queryset_methods(new.QUERYSET_METHODS_TO_EXTEND)
        return new


class BaseAbstractVersionControl(models.Model):
    """
    The base abstract model that provide methods for track model object changes
    """

    VERSION_MANAGER_ENABLED: bool = True  # a flag for turn on / off tracking by version manager
    WRITE_CHANGES: bool = True
    WRITE_CREATION: bool = True
    WRITE_DELETION: bool = True

    class Meta:
        abstract = True

    @classmethod
    def from_db(cls, db, field_names, values):
        # record initial state of fields
        instance = super().from_db(db, field_names, values)
        setattr(instance, "initial_field_names", field_names)
        setattr(instance, "initial_values", values)
        return instance

    def can_write_version(self) -> bool:
        is_allow_to_write_version = self.VERSION_MANAGER_ENABLED
        if self._state.adding:
            is_allow_to_write_version &= self.WRITE_CREATION
        elif self.check_changes():
            is_allow_to_write_version &= self.WRITE_CHANGES
        else:
            is_allow_to_write_version = False
        return is_allow_to_write_version

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # check for changes (or for adding an object)
        skip_handle_version = getattr(self, "skip_handle_version", False)
        need_write_history = not skip_handle_version and self.can_write_version()
        super().save(force_insert, force_update, using, update_fields)
        if need_write_history:
            self.handle_version()

    def handle_version(self, **kwargs) -> None:
        from version_control.service import get_version_manager_class

        # set object hash for debug info collector
        debugger_class = get_version_manager_debugger_class()
        debugger_class.HASH = self.get_hash()
        # main management
        manager_class = get_version_manager_class()
        manager = manager_class()
        # verify storage if it is not verified yet
        manager.provide_storage_verification()
        # adding an object to the temporary storage for further processing
        # If there is a 'request' - recording is done through temporary storage
        if manager.can_fill_storage():
            manager.add_object_to_storage(self, **kwargs)
        # If not, synchronously with saving the object (necessary when executing commands through manage.py)
        else:
            manager.create_version_from_objects(self, **kwargs)

    def get_hash(self) -> str:
        # get the hash value of the current object
        hash_data_string = f"{self.__class__.__name__}-{self.id}"
        return str(get_str_hash(hash_data_string, digest_size=5))

    def check_changes(self) -> bool:
        # check changes of the model object after the first initialization
        object_changed = False
        initial_field_names = getattr(self, "initial_field_names", None)
        initial_values = getattr(self, "initial_values", None)
        if initial_field_names and initial_values:
            current_values = tuple(self.__dict__.get(field_name) for field_name in initial_field_names)
            object_changed = current_values != initial_values
        return object_changed


class AbstractMetaVersionControl(BaseAbstractVersionControl, metaclass=VersionManagerMeta):
    """
    The abstract class for version management with auto managers handle
    """

    QUERYSET_METHODS_TO_EXTEND: tuple = ("update",)

    class Meta:
        abstract = True


class AbstractVersionControl(BaseAbstractVersionControl):

    """
    Main abstract class for version handling
    """

    class Meta:
        abstract = True
