# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0003_auto_20150514_0856'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendancelog',
            unique_together=set([('classroom', 'date')]),
        ),
    ]
