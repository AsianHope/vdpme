# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0010_auto_20150520_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academic',
            name='test_grade_khmer',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_grade_math',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='cohort',
            field=models.IntegerField(default=2014, verbose_name=b'Target Grade', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='endo',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='extractions',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='filling',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='pulped',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='scaling',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='sealent',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='xray',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
