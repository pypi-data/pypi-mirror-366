import json
import logging
import uuid
from typing import List, Optional, Type, Union

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.base import Serializer
from django.db import transaction
from django.urls import resolve
from django.utils import timezone

from version_control.cache import VersionControlTemporaryStorage, get_version_manager_storage_class
from version_control.collections import ModelObjectChangeType
from version_control.database import TransactionManager
from version_control.debugger import debug_method, get_version_manager_debugger_class
from version_control.middleware import get_request
from version_control.models import BaseAbstractVersionControl, ModelObjectVersion, ModelObjectVersionGroup
from version_control.serializers import (
    VersionControlJSONEncoder,
    VersionControlJSONSerializer,
    VersionControlLiteJSONSerializer,
    VersionControlPythonSerializer,
)
from version_control.utils import get_class_from_settings

logger = logging.getLogger(__name__)

USER_MODEL_CLASS = get_user_model()


def get_version_manager_class() -> Type["VersionControlManager"]:
    """
    Returns current version manager class from the project settings or original "VersionControlManager"
    """

    error_message = (
        'Не найден указанный в "settings" класс менеджера версий. Используется стандартный - ' '"VersionControlManager"'
    )
    return get_class_from_settings("VERSION_MANAGER_CLASS", error_message, VersionControlManager)


class VersionControlManager:
    """
    A main class for version manager
    """

    _CACHE_ENABLE_FLAG: str = "VERSION_MANAGER_CACHING_ENABLED"
    _SILENT_PROCESSING_FLAG: str = "VERSION_MANAGER_PROCESS_SILENT"
    _CUSTOM_STORAGE_PROCESSING_FLAG: str = "VERSION_MANAGER_CUSTOM_STORAGE_PROCESSING"

    def __init__(
        self,
        using=None,
        request_key: str = None,
        storage_timeout: int = 60,
        storage_class: Type[VersionControlTemporaryStorage] = None,
    ):
        self.using = using
        self.request = get_request()
        self.request_key = request_key or getattr(self.request, "key", None)
        self.current_user = getattr(self.request, "user", None)

        # storage
        self.storage_timeout = storage_timeout
        self.storage_class = storage_class or get_version_manager_storage_class()
        self.vcs_caching_enabled = getattr(settings, self._CACHE_ENABLE_FLAG, False)

        # check project settings variables
        self.process_silent = getattr(settings, self._SILENT_PROCESSING_FLAG, False)
        self.custom_storage_processing_enabled = getattr(settings, self._CUSTOM_STORAGE_PROCESSING_FLAG, False)

        # debug
        self.debugger_class = get_version_manager_debugger_class()

        # database
        database = "default" if self.using is None else self.using
        self.atomic_requests_enabled = settings.DATABASES[database]["ATOMIC_REQUESTS"]

        # manager cache
        self._unsaved_versions = []  # type: List[ModelObjectVersion]
        self.saved_versions = []  # type: List[ModelObjectVersion]

    @debug_method(prefix="---\n")
    def provide_storage_verification(self) -> None:
        """
        Sets verification flag for signatures stored in the version control temporary storage.
        If the project uses transactions, storage data marks as valid on exit the active transaction block,
        if the project doesn't use transactions - verification flag sets in changed object save method.
        Storage without verification flag will be considered as invalid and signatures stored in it will be never
        recorded.
        """

        if self.atomic_requests_enabled:
            connection = transaction.get_connection()
            if connection.in_atomic_block:
                transaction.on_commit(self.verify_storage)
        else:
            self.verify_storage()

    def get_storage(self) -> "VersionControlTemporaryStorage":
        return self.storage_class(storage_key=self.request_key, timeout=self.storage_timeout)

    @debug_method
    def can_fill_storage(self) -> bool:
        return bool(self.request_key) and self.vcs_caching_enabled

    @debug_method
    def can_process_storage(self) -> bool:
        storage = self.get_storage()
        return bool(self.request_key) and self.vcs_caching_enabled and storage.is_verified

    @debug_method
    def verify_storage(self) -> None:
        storage = self.get_storage()
        storage.verify()

    @staticmethod
    @debug_method
    def get_version_control_model_classes(to_str: bool = False) -> list:
        # obtain all tracking model classes
        return [
            model_class.__name__.lower() if to_str else model_class
            for model_class in apps.get_models()
            if issubclass(model_class, BaseAbstractVersionControl)
        ]

    @debug_method
    def initialize_version_control(
        self, vcs_datetime: Optional[timezone.datetime], print_progress: bool = True
    ) -> None:
        """
        Records initial versions for tracking objects
        """

        model_classes = self.get_version_control_model_classes()
        model_classes_len = len(model_classes)
        for index, model_class in enumerate(model_classes):
            model_class_objects = model_class.objects.all()
            created = timezone.localtime(timezone.make_aware(vcs_datetime)) if vcs_datetime is not None else None
            self.create_version_from_objects(
                *model_class_objects,
                version_created=created,
                version_change_type=ModelObjectChangeType.OBJECT_STATE_INIT,
                pre_populate_mode=True,
            )
            if print_progress:
                print(f"{index + 1}/{model_classes_len}: {model_class.__name__} всего: {model_class_objects.count()}")

    def get_current_app(self) -> str:
        return resolve(self.request.path).app_name if self.request else None

    def get_current_url(self) -> str:
        return self.request.get_full_path() if self.request else None

    @debug_method
    def add_object_to_storage(self, changed_object: Type[BaseAbstractVersionControl], **version_control_kwargs) -> None:
        """
        Adds object signature to temporary storage
        :param changed_object: object to add to the storage
        :param version_control_kwargs: parameters for version control service
        :return: None
        """

        # check "version_change_type" and set suitable serializer (fields data is not needed for versions of
        # deleted objects)
        serializer = VersionControlJSONSerializer
        if version_control_kwargs.get("version_change_type") == ModelObjectChangeType.OBJECT_DELETED:
            serializer = VersionControlLiteJSONSerializer

        storage = self.get_storage()
        serialized_object = self.serialize_objects(changed_object, serializer=serializer)
        changed_object_hash = changed_object.get_hash()
        version_control_kwargs.update(
            version_author=self.current_user,
            request_key=self.request_key,
            version_change_url=self.get_current_url(),
            version_change_app=self.get_current_app(),
        )
        storage.add_object(serialized_object, changed_object_hash, **version_control_kwargs)

    @debug_method
    def create_version_from_storage(self) -> List[ModelObjectVersion]:
        # get and load form the storage, and record objects signatures with specified parameters
        transaction_manager = TransactionManager(Exception, raise_exc=self.process_silent)
        transaction_manager.transaction_rollback_log_message = "Version Control transaction rollback: %s, %s"
        with transaction_manager:
            storage = self.get_storage()
            storage.clean()
            for object_hash, signature in storage.get_objects():
                # set object hash for debug info collector
                self.debugger_class.HASH = object_hash
                # load dumped to json and stored in storage object signature
                extracted_object = json.loads(signature["serialized_object"])[0]
                self.create_version_from_serialized(extracted_object, **signature["kwargs"])
                storage.remove_object_by_hash(object_hash)
            storage.flush()
            self.save_versions(bulk=True)
        return self.saved_versions

    @debug_method
    def create_version_from_serialized(
        self, serialized_object: dict, commit: bool = False, **kwargs
    ) -> Optional[List[ModelObjectVersion]]:
        """
        Creates versions for signatures loaded from the storage (serialized from json string to python dict)
        """

        skip_version_control = kwargs.pop("skip_version_control", False)
        if not skip_version_control:
            service_parameters = self.get_service_parameters(**kwargs)
            service = self.Service(serialized_object, **service_parameters)
            if service:
                new_version = service.init_version()
                if new_version is not None:
                    self._unsaved_versions.append(new_version)
        if commit:
            self.save_versions(bulk=True)
            return self.saved_versions

    @debug_method
    def create_version_from_objects(self, *changed_objects, **kwargs) -> List[ModelObjectVersion]:
        """
        Creates versions for collection of modified objects without caching
        :param changed_objects: collection of objects for writing versions
        :param kwargs: dict, parameters for version control service
        :return: List[ModelObjectVersion]
        """

        serialized_objects = self.serialize_objects(*changed_objects, serializer=VersionControlPythonSerializer)
        for serialized_object in serialized_objects:
            self.create_version_from_serialized(serialized_object, **kwargs)
        self.save_versions(bulk=True)
        return self.saved_versions

    @debug_method
    def save_versions(self, bulk: bool = False) -> None:
        # save created versions of model objects
        if self._unsaved_versions:
            if bulk:
                self.saved_versions += ModelObjectVersion.objects.bulk_create(self._unsaved_versions)
            else:
                for version in self._unsaved_versions:
                    version.save()
                    self.saved_versions.append(version)
            self._unsaved_versions.clear()

    def get_service_parameters(self, **kwargs):
        service_parameters = dict()
        service_parameters["version_author"] = kwargs.pop("version_author", self.current_user)
        service_parameters["version_request_key"] = kwargs.pop("request_key", self.request_key)
        service_parameters["version_change_type"] = kwargs.pop("version_change_type", None)
        service_parameters["version_change_url"] = kwargs.pop("version_change_url", self.get_current_url())
        service_parameters["version_change_app"] = kwargs.pop("version_change_app", self.get_current_app())
        service_parameters["version_created"] = kwargs.pop("version_created", None)
        service_parameters["pre_populate_mode"] = kwargs.pop("pre_populate_mode", False)
        return service_parameters

    def revert_model_object_version(self, target_version_hash: str) -> None:
        """
        Rolls back the model object version
        :param target_version_hash: version hash for rollback
        :return: None
        """

        target_version = ModelObjectVersion.objects.filter(hash=target_version_hash).first()
        if target_version and not target_version.is_last_version():
            if target_version.state is None:
                pass
            else:
                (
                    deserialized_object,
                    proxy_object,
                ) = target_version.get_state_deserialized()
                if deserialized_object and proxy_object:
                    deserialized_object.save()
                    self.create_version_from_objects(
                        proxy_object.object,
                        version_change_type=ModelObjectChangeType.OBJECT_RESTORED,
                    )

    @classmethod
    @debug_method
    def serialize_objects(
        cls,
        *changed_objects,
        serializer: Type[Serializer] = VersionControlJSONSerializer,
    ) -> dict:
        return serializer().serialize(changed_objects)

    class Service:
        """
        A service class for recording versions of modified model objects
        """

        def __init__(
            self,
            serialized_object: dict,
            version_author: Union[USER_MODEL_CLASS, int] = None,
            version_request_key: uuid = None,
            version_change_type: str = None,
            version_change_url: str = None,
            version_change_app: str = None,
            version_created: timezone.datetime = None,
            pre_populate_mode: bool = False,
        ):
            self.serialized_object = serialized_object
            self.version_author = version_author
            self.version_request_key = version_request_key or uuid.uuid4().hex
            self.version_change_type = version_change_type
            self.version_change_url = version_change_url
            self.version_change_app = version_change_app
            self.version_created = version_created or timezone.now()
            self.version_hash = uuid.uuid4().hex
            self.pre_populate_mode = pre_populate_mode
            self.group, self.is_first_version_init = self.init_version_group()

        @debug_method(prefix="---\n")
        def init_version_group(self) -> tuple:
            # extract info for "ModelObjectsVersionGroup" creation
            extracted_model = self.serialized_object["model"].split(".")[-1]
            return ModelObjectVersionGroup.objects.get_or_create(
                content_type=ContentType.objects.filter(model=extracted_model).first(),
                object_id=self.serialized_object["pk"],
                defaults=dict(
                    representation=self.serialized_object["obj_extra_data"]["representation"],
                    verbose_name=self.serialized_object["obj_extra_data"]["verbose_name"],
                ),
            )

        @debug_method
        def init_version(self) -> ModelObjectVersion:
            version = None
            need_pre_population = self.pre_populate_mode and (
                self.is_first_version_init or not self.group.model_object_versions.exists()
            )
            if not self.pre_populate_mode or need_pre_population:
                version = ModelObjectVersion(
                    group=self.group,
                    request_key=self.version_request_key,
                    created=self.version_created,
                    change_url=self.version_change_url,
                    change_app=self.version_change_app,
                    hash=self.version_hash,
                    change_type=self.get_version_change_type(),
                    state=self.get_dumped_state(),
                )

                # User set. When set to 'None', it is considered that the change was made by the system
                if isinstance(self.version_author, int):
                    version.author_id = self.version_author
                elif isinstance(self.version_author, USER_MODEL_CLASS):
                    version.author = self.version_author
            return version

        def get_version_change_type(self) -> str:
            version_change_type = self.version_change_type
            if version_change_type is None:
                if self.is_first_version_init:
                    version_change_type = ModelObjectChangeType.OBJECT_CREATED
                else:
                    version_change_type = ModelObjectChangeType.OBJECT_CHANGED
            return version_change_type

        @debug_method
        def get_dumped_state(self) -> str:
            # dump modified object to json string for saving to 'JSONField'
            # we can store the original python dict "self.serialized_object", but in this case there will be problems
            # with "datetime" deserialization
            # to prevent that we dump dict to json string with using "VersionControlJSONEncoder" as encoder
            return json.dumps(self.serialized_object, cls=VersionControlJSONEncoder)
