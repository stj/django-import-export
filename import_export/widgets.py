from __future__ import unicode_literals

from decimal import Decimal
from datetime import datetime
from datetime import timedelta

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class Widget(object):
    """
    Widget takes care of converting between import and export representations.

    Widget objects have two functions:

    * converts object field value to export representation

    * converts import value and converts it to appropriate python
      representation
    """
    def __init__(self, field):
        self.field = field

    def clean(self, value):
        """
        Returns appropriate python objects for import value.
        """
        return value

    def render(self, value):
        """
        Returns export representation of python value.
        """
        return force_text(value)


class IntegerWidget(Widget):
    """
    Widget for converting integer fields.
    """

    def clean(self, value):
        if not value:
            return None
        return int(value)


class DecimalWidget(Widget):
    """
    Widget for converting decimal fields.
    """

    def clean(self, value):
        if not value:
            return None
        return Decimal(value)

    def render(self, value):
        return format(value, '%d.%df' % (self.field.max_digits,
                                         self.field.decimal_places))


class CharWidget(Widget):
    """
    Widget for converting text fields.
    """

    def render(self, value):
        return force_text(value)


class BooleanWidget(Widget):
    """
    Widget for converting boolean fields.
    """
    TRUE_VALUES = ["1", 1]
    FALSE_VALUE = "0"

    def render(self, value):
        return self.TRUE_VALUES[0] if value else self.FALSE_VALUE

    def clean(self, value):
        return True if value in self.TRUE_VALUES else False


# start one day before 1900-0-0 to handle excels added leap year 1990
epoch = datetime(1899, 12, 30, 0, 0, 0)


class DateWidget(Widget):
    """
    Widget for converting date fields.

    Takes optional ``format`` parameter.

    If value is a float will assume an excel date.
    http://www.cpearson.com/excel/datetime.htm
    """

    def __init__(self, format=None, *args, **kwargs):
        super(DateWidget, self).__init__(*args, **kwargs)
        if format is None:
            format = "%Y-%m-%d"
        self.format = format

    def clean(self, value):
        if not value:
            return None
        elif isinstance(value, float):
            dt = epoch + timedelta(seconds=60 * 60 * 24 * value)
            return dt.date()
        return datetime.strptime(value, self.format).date()

    def render(self, value):
        return value.strftime(self.format)


class DateTimeWidget(Widget):
    """
    Widget for converting date fields.

    Takes optional ``format`` parameter.

    If value is a float will assume an excel date.
    http://www.cpearson.com/excel/datetime.htm
    """

    def __init__(self, format=None, *args, **kwargs):
        super(DateTimeWidget, self).__init__(*args, **kwargs)
        if format is None:
            format = "%Y-%m-%d %H:%M:%S"
        self.format = format

    def clean(self, value):
        if not value:
            return None
        elif isinstance(value, float):
            return epoch + timedelta(seconds=60 * 60 * 24 * value)
        return datetime.strptime(value, self.format)

    def render(self, value):
        return value.strftime(self.format)


class ForeignKeyWidget(Widget):
    """
    Widget for ``ForeignKey`` model field that represent ForeignKey as
    integer value.

    Requires a positional argument: the class to which the field is related.
    """

    def __init__(self, *args, **kwargs):
        super(ForeignKeyWidget, self).__init__(*args, **kwargs)
        self.model = self.field.rel.to
        self.to_field = self.field.rel.field_name

    def clean(self, value):
        value = super(ForeignKeyWidget, self).clean(value)
        return value or None

    def render(self, value):
        if value is None:
            return ""
        return getattr(value, self.to_field, value)


class ManyToManyWidget(Widget):
    """
    Widget for ``ManyToManyField`` model field that represent m2m field
    as comma separated pk values.

    Requires a positional argument: the class to which the field is related.
    """

    def __init__(self, *args, **kwargs):
        super(ManyToManyWidget, self).__init__(*args, **kwargs)
        self.model = self.field.rel.to

    def clean(self, value):
        if not value:
            return self.model.objects.none()
        ids = value.split(",")
        return self.model.objects.filter(pk__in=ids)

    def render(self, value):
        ids = [str(obj.pk) for obj in value.all()]
        return ",".join(ids)
