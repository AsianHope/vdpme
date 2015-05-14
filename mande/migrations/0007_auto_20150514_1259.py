# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0006_classroom_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='active',
            field=models.BooleanField(default=True, verbose_name=b'Takes Attendance'),
            preserve_default=True,
        ),
    ]
