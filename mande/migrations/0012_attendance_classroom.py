# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0011_auto_20150525_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='classroom',
            field=models.ForeignKey(blank=True, to='mande.Classroom', null=True),
            preserve_default=True,
        ),
    ]
