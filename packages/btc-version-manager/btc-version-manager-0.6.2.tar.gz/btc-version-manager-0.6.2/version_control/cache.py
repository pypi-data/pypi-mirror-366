import logging
from collections import OrderedDict
from typing import Hashable, Optional, Type

from django.core.cache import cache

from version_control.utils import get_class_from_settings

logger = logging.getLogger(__name__)


def get_version_manager_storage_class() -> Type["VersionControlTemporaryStorage"]:
    """
    Returns current version control storage class from the project settings or original "VersionControlTemporaryStorage"
    """

    error_message = (
        'Не найден указанный в "settings" класс менеджера версий. Используется стандартный - '
        '"VersionControlTemporaryStorage"'
    )
    return get_class_from_settings("VERSION_MANAGER_STORAGE_CLASS", error_message, VersionControlTemporaryStorage)


class VersionControlTemporaryStorage:
    """
    The temporary storage class. The storage should contain objects that require version control.
    That storage is a wrapper over a regular dictionary that can be cached by project cache backend and restored from
    it at anytime by the unique key 'request_key'.
    The storage contains all necessary data for writing versions and can be processed in other processes (celery).
    The 'is_verified' flag sets on active transaction commit, the 'is_cleaned' flag designed to verify completion of
    additional storage processing (if specified) before writing versions. Both flags must be set to 'True' for
    versions recording.
    """

    EMPTY_STORAGE_DATA: dict = dict(is_verified=False, is_cleaned=False, changed_objects={})
    __STORAGE: OrderedDict = OrderedDict(EMPTY_STORAGE_DATA)

    def __init__(self, storage_key: Hashable, timeout: int = 60):
        self.storage_key = storage_key
        self.timeout = timeout

    @property
    def storage(self) -> OrderedDict:
        return self.__class__.__STORAGE

    @storage.setter
    def storage(self, value: OrderedDict) -> None:
        self.__class__.__STORAGE = value

    def cache_storage(self) -> None:
        cache.set(self.storage_key, self.storage, timeout=self.timeout)

    def flush(self) -> None:
        self.storage = OrderedDict(self.EMPTY_STORAGE_DATA)
        self.cache_storage()

    @property
    def is_verified(self) -> bool:
        # check whether it is possible to record versions for storage data
        return self.storage["is_verified"]

    @is_verified.setter
    def is_verified(self, state: bool) -> None:
        self.storage["is_verified"] = state

    @property
    def is_cleaned(self) -> bool:
        # check if storage is prepared before retrieving modified objects
        return self.storage["is_cleaned"]

    @is_cleaned.setter
    def is_cleaned(self, state: bool) -> None:
        # set the storage ready flag
        self.storage["is_cleaned"] = state

    def add_object(self, serialized_object: dict, changed_object_hash: str, **version_control_kwargs) -> None:
        """
        Method for adding an object to the storage.
        :param serialized_object: serialized state of the object to add to the storage
        :param changed_object_hash: hash of an object to identify it in the storage
        :param version_control_kwargs: parameters for version control service
        :return: None
        """

        changed_object_signature = {
            changed_object_hash: {
                "serialized_object": serialized_object,
                "kwargs": version_control_kwargs,
            }
        }
        self.storage["changed_objects"].update(changed_object_signature)

    def get_object_by_hash(self, object_hash: str) -> dict:
        return self.storage["changed_objects"].get(object_hash)

    def remove_object_by_hash(self, object_hash: str) -> Optional[dict]:
        removed = self.storage["changed_objects"].pop(object_hash)
        return removed

    def get_objects(self) -> dict:
        storage_data = dict()
        if self.is_verified and self.is_cleaned:
            # retrieve objects signatures from storage
            storage_data = self.storage["changed_objects"].copy().items()
        return storage_data

    def clean(self) -> None:
        # dummy method, prepare stored objects here
        self.is_cleaned = True

    def verify(self) -> None:
        # verification of the storage
        self.is_verified = True
