from typing import Any, Collection

from django.db import models
from django.forms import model_to_dict

from version_control.collections import ModelObjectChangeType


class VersionManagerDiffChecker:
    """
    A checker for displaying versions difference
    """

    DISPLAY_VALUE_FOR_DELETED = "УДАЛЕНО"
    MISSED_FIELD_MESSAGE = "Не удалось найти поле в этой версии"

    def __init__(self, versions):
        self.versions = versions
        self.version_proxies = [version.get_version_proxy() for version in versions if version]
        self.field_names = self.get_common_field_names()

        self._actual_changes = []

    @property
    def actual_changes(self) -> list:
        # cached property for getting changes list
        if not self._actual_changes:
            self._actual_changes = [row for row in self.get_rows() if row]
        return self._actual_changes

    def get_rows(self) -> list:
        for field_name in self.field_names:
            field_data_dict = dict()
            field_verbose_name = self.get_verbose_name(field_name)

            if field_verbose_name:
                field_data_dict[field_verbose_name] = row_data = dict()
                for index, proxy in enumerate(self.version_proxies):
                    if proxy.version.change_type != ModelObjectChangeType.OBJECT_DELETED:
                        proxy_field = proxy.fields.get(field_name)
                        value = getattr(proxy_field, "value", self.MISSED_FIELD_MESSAGE)
                    else:
                        value = self.DISPLAY_VALUE_FOR_DELETED

                    row_data[index] = value

                unique_values = set([str(value) for value in field_data_dict.get(field_verbose_name, {}).values()])
                # check for diffs, if there are diffs append them as rows
                if len(self.version_proxies) == 1 or len(unique_values) > 1:
                    yield field_data_dict

    def get_common_field_names(self) -> set:
        field_names = []

        if self.version_proxies:
            content_type = self.version_proxies[0].version.group.content_type
            model_class = content_type.model_class()
            if model_class:
                field_names = [field.name for field in model_class._meta.get_fields()]
            else:
                field_names = []
                for proxy in self.version_proxies:
                    state = proxy.version.get_state()
                    state_field_names = state["fields"].keys() if state else []
                    field_names.extend(state_field_names)

        return set(field_names)

    def get_verbose_name(self, field_name: str, reserve_name: str = None) -> str:
        verbose_name = None

        for proxy in self.version_proxies:
            proxy_field = proxy.fields.get(field_name)

            verbose_name = getattr(proxy_field, "verbose_name", None)
            if verbose_name:
                break
            if reserve_name is None:
                reserve_name = getattr(proxy_field, "name", None)

        return verbose_name or reserve_name

    def get_plain_diff(self) -> tuple:
        """
        Returns diff as tuple: ((field_name, first_version_field_value, ..., n_version_field_value), ...)
        """

        for row in self.get_rows():
            if row:
                for field_name, diff in row.items():
                    changes_row = (field_name,)
                    for col, field_value in diff.items():
                        changes_row += (field_value,)
                    yield changes_row


class VersionProxy:
    """
    A helper class for storing temporary version data
    """

    def __init__(self, version: "ModelObjectVersion", fields: dict):
        self.version = version
        self.fields = fields


class VersionProxyField:
    """
    A helper class for storing temporary fields data of changed objects
    """

    def __init__(self, name: str, value: Any, field_extra_data: dict):
        self.name = name
        self.verbose_name = field_extra_data.get("verbose_name", name)
        self.internal_type = field_extra_data.get("internal_type")
        self.field_extra_data = field_extra_data
        self.value = self.cast_value(self.internal_type, value)

    def cast_value(self, internal_type: str, value: Any, default: Any = "-") -> Any:
        prepared_value = None
        bad_values = (None, "", " ")

        if value is not None:
            # TODO: add date / datetime transform
            # if internal_type == 'DateTimeField':
            #     prepared_value = format_date(value, "d.m.Y H:i")
            # elif internal_type == 'DateField':
            #     prepared_value = format_date(value)
            if internal_type == "BooleanField":
                prepared_value = "Да" if value else "Нет"
            elif internal_type in ["CharField", "ArrayField"]:
                prepared_value = self.field_extra_data.get("display_value", value)
            elif internal_type in ["ForeignKey", "ManyToManyField"]:
                prepared_value = self.field_extra_data.get("representation", value)
            else:
                prepared_value = value

        return prepared_value if prepared_value not in bad_values else default


class VersionWrapper:
    """
    A helper wrapper class over modified object
    """

    def __init__(self, model_object: models.Model):
        self.state = model_to_dict(model_object)

    def __eq__(self, other: "VersionWrapper"):
        return not bool(self.__sub__(other))

    def __ne__(self, other: "VersionWrapper"):
        return bool(self.__sub__(other))

    def __sub__(self, other: "VersionWrapper"):
        return self.get_diff(self.state, other.state)

    @staticmethod
    def get_diff(start_state: dict, next_state: dict, check_fields: Collection = None):
        # Get changed fields of an object
        changed_fields = dict()
        common_dict_keys = set(start_state) & set(next_state)
        fields_for_check = check_fields or common_dict_keys
        for key in common_dict_keys:
            if key in fields_for_check and start_state[key] != next_state[key]:
                changed_fields[key] = dict(start_state=start_state[key], next_state=next_state[key])
        return changed_fields
