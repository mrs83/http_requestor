"""Custom Django fields."""

import json

from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder


class JSONField(models.TextField):
    """
    Add's JSON capabilities (retrieval) to Django's TextField.

    NOTE: It makes use of the Standard json module.
    """

    description = """Database Agnostic JSON field
    It allows you to enter use Standard JSON style (Double quotes)
    or single quotes (Python dicts representation).
    """

    def __init__(self, *args, **kwargs):
        kwargs['default'] = '{}'
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        """Convert single quotes to double quotes to make the JSON valid."""
        valid_json = value.replace("'", '"')

        return super(JSONField, self).clean(valid_json, model_instance)

    def from_db_value(self, value, expression, connection, *args, **kwargs):
        """Convert the JSON from the database to a dictionary."""
        return self.to_python(value)

    def get_prep_value(self, value):
        """Convert the dictionary to JSON, which is saved as text."""
        prep_value = super(JSONField, self).get_prep_value(value)

        return json.dumps(prep_value, cls=DjangoJSONEncoder)

    def to_python(self, value):
        """Convert JSON to a python dictionary"""
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise ValidationError(_('Invalid JSON: {}'.format(str(error))))
        except TypeError:
            return value
