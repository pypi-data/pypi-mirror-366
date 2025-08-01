import django.dispatch
from django.core.signals import request_finished
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from version_control.collections import ModelObjectChangeType
from version_control.debugger import get_version_manager_debugger_class
from version_control.models import BaseAbstractVersionControl
from version_control.service import get_version_manager_class

can_process_storage_signal = django.dispatch.Signal()


@receiver(pre_delete)
def handle_version_control_on_obj_delete(sender, instance, **kwargs):
    """
    Processing a signal to delete an object (instead of the model delete () - method for tracking
    cascading delete)
    """

    if issubclass(sender, BaseAbstractVersionControl):
        if instance.WRITE_DELETION:
            instance.handle_version(version_change_type=ModelObjectChangeType.OBJECT_DELETED)


@receiver(request_finished)
def handle_version_control_on_request_finished(sender, **kwargs):
    """
    Function that process "request_finished" signal to start recording versions from temporary storage
    "VersionControlTemporaryStorage" or specified in the settings.
    Processing through celery is possible.
    """

    manager_class = get_version_manager_class()
    manager = manager_class()
    if manager.can_process_storage():
        # process the storage if it can be processed and "_CUSTOM_STORAGE_PROCESSING_FLAG" is not set to "True"
        if not manager.custom_storage_processing_enabled:
            manager.create_version_from_storage()
        else:
            # send signal if the version manager storage can be processed
            can_process_storage_signal.send(sender=manager_class, request_key=manager.request_key)

    debugger_class = get_version_manager_debugger_class()
    debugger_class.log_report()
