import argparse
import logging
import sys
import uuid
from copy import deepcopy
from typing import Any, Optional

from _blake2 import blake2b
from django.conf import settings
from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.db.models import Model
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.timezone import datetime as dt

logger = logging.getLogger(__name__)


# region BTC version manager date/datetime formatting


def make_datetime_from_string(
    datetime_string: str,
    datetime_string_format: str = "%d.%m.%Y %H:%i",
    exception_class: Any = None,
) -> Optional[dt]:
    """
    Function that extracts 'datetime' object from string
    :param datetime_string: string with date and time
    :param datetime_string_format: date and time string format for conversion
    :param exception_class: exception class
    :return: Optional[dt]
    """

    invalid_datetime_string_message = f"{datetime_string}: невалидные дата и время"
    datetime_object = None

    try:
        datetime_object = dt.strptime(datetime_string, datetime_string_format)
    except ValueError:
        if exception_class is not None:
            raise exception_class(invalid_datetime_string_message)
    return datetime_object


def make_date_for_arg_parse(date_string: str) -> Optional[dt]:
    """
    Function that returns a formatted date for the parser 'argparse'
    :param date_string: str, string with date
    :return: Optional[dt]
    """

    invalid_date_string_message = f"{date_string}: невалидная дата"
    return make_datetime_from_string(
        date_string,
        datetime_string_format="%d.%m.%Y",
        exception_class=argparse.ArgumentTypeError(invalid_date_string_message),
    )


def make_time_for_arg_parse(time_string: str) -> Optional[dt]:
    """
    Function that returns formatted time for parser 'argparse'
    :param time_string: string with time
    :return: Optional[dt]
    """

    invalid_date_string_message = f"{time_string}: невалидное время"
    return make_datetime_from_string(
        time_string,
        datetime_string_format="%H:%M",
        exception_class=argparse.ArgumentTypeError(invalid_date_string_message),
    )


def format_date(date: Any, output_format: str = "d.m.Y", default: Any = "") -> Any:
    """
    Function that returns formatted datetime object
    """

    if date is not None:
        if isinstance(date, timezone.datetime) and timezone.is_aware(date):
            date = timezone.localtime(date)
        return date_format(date, output_format)
    return default


# endregion


# region BTC version manager UUID mapping/hashing


def get_uuid_from_string(convert_string: str, use_namespace: uuid = uuid.NAMESPACE_DNS) -> uuid:
    """
    Function that converts string to uuid
    """

    return uuid.uuid5(use_namespace, convert_string)


def get_str_hash(data_string: str, digest_size: int) -> blake2b:
    """
    Function for hash generating hash
    :param data_string: string to convert
    :param digest_size: maximum number of bytes
    :return: blake2b
    """

    result_hash = blake2b(digest_size=digest_size)
    result_hash.update(data_string.encode())
    return result_hash.hexdigest()


# endregion


# region BTC version manager admin features


def build_vcs_relation_tree(parent_object: Model) -> tuple:
    """
    Method for forming a cascading tree of child objects
    :param parent_object: parent to form a tree
    :return: tuple, nested lists of 'parent_object' relation objects
    """

    version_manager_enabled_flag = "VERSION_MANAGER_ENABLED"

    vcs_tree = []
    vcs_missed_objects_tree = []

    if parent_object:
        using = router.db_for_write(parent_object._meta.model)
        collector = NestedObjects(using=using)
        collector.collect((parent_object,))

        def prepare_relations(collector_object: NestedObjects, get_missed: bool = False) -> NestedObjects:
            """
            Helper function for preparing a selection of child objects
            :param collector_object: collector object
            :param get_missed: flag to display only unconnected objects
            :return: NestedObjects
            """

            collector_copy = deepcopy(collector_object)
            for key, relations in deepcopy(collector_copy.edges).items():
                for value in relations:
                    is_vcs_object = hasattr(value, version_manager_enabled_flag)
                    # version manager models must be ignored
                    is_vcs_service_obj = value.__class__.__name__ in [
                        "ModelObjectVersionGroup",
                        "ModelObjectVersion",
                    ]
                    if (
                        get_missed
                        and key
                        and is_vcs_object
                        or not get_missed
                        and not is_vcs_object
                        or is_vcs_service_obj
                    ):
                        collector_copy.edges[key].remove(value)
            return collector_copy

        def format_callback(obj: Model) -> str:
            """
            Function for preparing formatted output of objects in the relationship tree
            :param obj: tree element object
            :return: str
            """

            opts = obj._meta
            formatted_value = f"{capfirst(opts.verbose_name)}: {obj}"

            if hasattr(obj, version_manager_enabled_flag):
                try:
                    url_arg = f"{opts.app_label}/{opts.model_name}/{obj.id}"
                    vcs_url = reverse(
                        "admin:version_control_modelobjectversiongroup_change",
                        args=(url_arg,),
                    )
                    formatted_value = format_html(
                        '{}: <a href="{}" target="_blank">{}</a>',
                        capfirst(opts.verbose_name),
                        vcs_url,
                        obj,
                    )
                except NoReverseMatch:
                    pass

            return formatted_value

        vcs_tree = prepare_relations(collector).nested(format_callback)
        vcs_missed_objects_tree = prepare_relations(collector, get_missed=True).nested(format_callback)

    return vcs_tree, vcs_missed_objects_tree


# endregion


# region BTC version manager class handlers


def get_class_from_path(path: str, split_symbol: str = ".") -> Any:
    class_object = None
    if path and split_symbol in path:
        class_path = path.rsplit(split_symbol, 1)
        module = sys.modules.get(class_path[0])
        class_object = getattr(module, class_path[1], None)
    return class_object


def get_class_from_settings(settings_var_name: str, error_message: str, default: Any) -> Any:
    class_path_from_settings = getattr(settings, settings_var_name, None)
    class_from_settings = get_class_from_path(class_path_from_settings)
    if class_path_from_settings and not class_from_settings:
        logger.error(error_message)
    return class_from_settings or default


# endregion
