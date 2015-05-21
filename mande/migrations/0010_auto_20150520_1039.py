# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0009_auto_20150514_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelog',
            name='date',
            field=models.DateField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='minors_encouraged',
            field=models.CharField(default=b'NA', max_length=2, verbose_name=b'Did you encourage them to take this job?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='minors_training',
            field=models.CharField(default=b'NA', max_length=2, verbose_name=b'Did they receive any vocational training?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')]),
            preserve_default=True,
        ),
    ]
