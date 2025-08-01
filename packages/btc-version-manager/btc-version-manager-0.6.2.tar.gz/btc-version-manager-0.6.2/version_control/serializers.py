import logging
from collections import OrderedDict
from typing import Type

from django.core.serializers import base, json, python
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Field, Model

logger = logging.getLogger(__name__)


class VersionControlBaseSerializer(base.Serializer):
    """
    The base serializer for version control objects.
    Designed for creating a recoverable representation of a modified object, as well as forwarding additional
    data for displaying information about changed fields

    Fixture structure:

    [
        {
            model: '',
            pk: '',
            fields: {
                'name_1': 'value_of_name_1',
                'name_2': 'value_of_name_2'
            },
            fields_extra_data: {
                'name_1': {
                    'verbose_name': 'verbose_name_of_name_1'
                    'internal_type': 'CharField',
                    'display_value': 'display_value_of_name_1'  If the field has an attribute 'choices'
                },
                'name_2': {
                    'verbose_name': 'verbose_name_of_name_2'
                    'internal_type': 'ForeignKey',
                    'representation': 'repr_of_name_2_fk'  a string representation of ForeignKey / ManyToManyField
                }
            },
            obj_extra_data: {
                'verbose_name': 'verbose_name_of_model_object',
                'representation': 'repr_of_model_object'  a string representation of tracking object
            }
        },
        {
            ...
        }
    ]
    """

    _fields_extra_data = None

    def start_serialization(self):
        super().start_serialization()
        self._fields_extra_data = None

    def start_object(self, obj):
        super().start_object(obj)
        self._fields_extra_data = OrderedDict()

    def end_object(self, obj):
        super().end_object(obj)
        self._fields_extra_data = None

    def get_dump_object(self, obj):
        data = super().get_dump_object(obj)
        data["fields_extra_data"] = self._fields_extra_data
        self.provide_obj_extra_data(data, obj)
        return data

    def handle_field(self, obj, field):
        super().handle_field(obj, field)
        self.provide_extra_data(obj, field)

    def handle_fk_field(self, obj, field):
        super().handle_fk_field(obj, field)
        self.provide_extra_data(obj, field)

    def handle_m2m_field(self, obj, field):
        super().handle_m2m_field(obj, field)
        self.provide_extra_data(obj, field)

    def provide_obj_extra_data(self, data, obj):
        # provide additional data
        data["obj_extra_data"] = obj_data = OrderedDict()
        obj_data["verbose_name"] = obj._meta.verbose_name
        obj_data["representation"] = str(obj)

    def provide_extra_data(self, obj, field):
        # fill the fixture with additional field data
        field_data = self._fields_extra_data.get(field.name)
        if not field_data:
            self._fields_extra_data[field.name] = field_data = dict()

        # writing a readable value and type for a field
        field_data["verbose_name"] = getattr(field, "verbose_name", field.name)
        field_data["internal_type"] = field.get_internal_type()

        # writing readable values for fields with the 'choices' property
        display_value = self.get_choice_field_display_value(obj, field)
        if display_value is not None:
            field_data["display_value"] = display_value

        # writing readable values for 'ForeignKey' and 'ManyToManyField' instead of pk values
        representation = self.get_representation(obj, field)
        if representation:
            field_data["representation"] = representation

    def get_choice_field_display_value(self, obj: Type[Model], field: Field) -> str:
        # retrieve translated display of field value 'display_value'
        display_value = None
        internal_type = field.get_internal_type()
        if internal_type in ["CharField", "ArrayField"] and hasattr(field, "choices"):
            field_value = getattr(obj, field.name, None)
            choices = dict(field.choices or ())
            if isinstance(field_value, str):
                display_value = choices.get(field_value, field_value)
            elif isinstance(field_value, list):  # ArrayField
                display_value = ", ".join([str(choices.get(value_item, value_item)) for value_item in field_value])
        return display_value

    def get_representation(self, obj: Type[Model], field: Field):
        representation = None

        # Possible inconsistent relations between children objects during cascading deletion and some ForeignKey
        # fields may don't have a value. In this case "ObjectDoesNotExist" exception is possible

        try:
            # extract descriptive names for field objects 'ForeignKey', 'ManyToManyField'
            internal_type = field.get_internal_type()
            if internal_type == "ForeignKey":
                representation = str(getattr(obj, field.name))
            elif internal_type == "ManyToManyField":
                representation = [str(related) for related in getattr(obj, field.name).iterator()]
        except Exception as e:
            logger.error(e)

        return representation


class VersionControlLiteBaseSerializer(VersionControlBaseSerializer):
    """
    The base serializer for version control objects for lite serialization.
    Skips fields serialization.
    """

    def handle_field(self, obj, field):
        self._current[field.name] = None

    def handle_fk_field(self, obj, field):
        self._current[field.name] = None

    def handle_m2m_field(self, obj, field):
        self._current[field.name] = None


class VersionControlLitePythonSerializer(VersionControlLiteBaseSerializer, python.Serializer):
    """
    A class for lite dict serializer
    """

    pass


class VersionControlLiteJSONSerializer(VersionControlLiteBaseSerializer, json.Serializer):
    """
    A class for lite json serializer
    """

    pass


class VersionControlPythonSerializer(VersionControlBaseSerializer, python.Serializer):
    """
    A class for dict serializer
    """

    pass


class VersionControlJSONSerializer(VersionControlBaseSerializer, json.Serializer):
    """
    A class for json serializer
    """

    pass


class VersionControlJSONEncoder(DjangoJSONEncoder):
    """
    An encoder class for "json" format
    """

    pass
