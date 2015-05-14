# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0002_attendancelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancelog',
            name='absent',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendancelog',
            name='present',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
