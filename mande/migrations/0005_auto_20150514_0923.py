# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0004_auto_20150514_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelog',
            name='date',
            field=models.DateField(auto_now=True),
            preserve_default=True,
        ),
    ]
