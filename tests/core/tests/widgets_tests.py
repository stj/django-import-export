from __future__ import unicode_literals

from decimal import Decimal
from datetime import date
from datetime import datetime

from django.test import TestCase

from import_export import widgets

from core.models import (
        Author,
        Category,
        )


class BooleanWidgetTest(TestCase):

    def setUp(self):
        self.widget = widgets.BooleanWidget()

    def test_clean(self):
        self.assertTrue(self.widget.clean("1"))
        self.assertTrue(self.widget.clean(1))


class DateWidgetTest(TestCase):

    def setUp(self):
        self.date = date(2012, 8, 13)
        self.widget = widgets.DateWidget('%d.%m.%Y')

    def test_render(self):
        self.assertEqual(self.widget.render(self.date), "13.08.2012")

    def test_clean(self):
        self.assertEqual(self.widget.clean("13.08.2012"), self.date)
        self.assertEqual(self.widget.clean(41134.0), self.date)


class DateTimeWidgetTest(TestCase):

    def setUp(self):
        self.dt = datetime(2012, 8, 13, 8, 13, 32)
        self.widget = widgets.DateTimeWidget('%d.%m.%Y %H:%M:%S')

    def test_render(self):
        self.assertEqual(self.widget.render(self.dt), "13.08.2012 08:13:32")

    def test_clean(self):
        self.assertEqual(self.widget.clean("13.08.2012 08:13:32"), self.dt)
        self.assertEqual(self.widget.clean(41134.342731481475), self.dt)


class DecimalWidgetTest(TestCase):

    def test_clean(self):
        widget = widgets.DecimalWidget()
        self.assertEqual(widget.clean("11.111"), Decimal("11.111"))
        self.assertEqual(widget.clean(""), None)


class ForeignKeyWidgetTest(TestCase):

    def setUp(self):
        self.widget = widgets.ForeignKeyWidget(Author)
        self.author = Author.objects.create(name='Foo')

    def test_clean(self):
        self.assertEqual(self.widget.clean(1), self.author.pk)

    def test_clean_empty(self):
        self.assertEqual(self.widget.clean(""), None)

    def test_render(self):
        self.assertEqual(self.widget.render(self.author), self.author.pk)

    def test_render_empty(self):
        self.assertEqual(self.widget.render(None), "")


class ManyToManyWidget(TestCase):

    def setUp(self):
        self.widget = widgets.ManyToManyWidget(Category)
        self.cat1 = Category.objects.create(name='Cat 1')
        self.cat2 = Category.objects.create(name='Cat 2')

    def test_clean(self):
        value = "%s,%s" % (self.cat1.pk, self.cat2.pk)
        cleaned_data = self.widget.clean(value)
        self.assertEqual(len(cleaned_data), 2)
        self.assertIn(self.cat1, cleaned_data)
        self.assertIn(self.cat2, cleaned_data)

    def test_render(self):
        self.assertEqual(self.widget.render(Category.objects),
                "%s,%s" % (self.cat1.pk, self.cat2.pk))
