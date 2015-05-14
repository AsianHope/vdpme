# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0007_auto_20150514_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelog',
            name='absent',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='present',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
