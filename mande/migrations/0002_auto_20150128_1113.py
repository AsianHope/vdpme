# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academic',
            name='test_grade_khmer',
            field=models.IntegerField(default=70, max_length=3, choices=[(99, b'A+'), (95, b'A'), (90, b'A-'), (89, b'B+'), (85, b'B'), (80, b'B-'), (79, b'C+'), (75, b'C'), (70, b'C-'), (69, b'D+'), (65, b'D'), (60, b'D-'), (50, b'F'), (0, b'I'), (999, b'NA')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_grade_math',
            field=models.IntegerField(default=70, max_length=3, choices=[(99, b'A+'), (95, b'A'), (90, b'A-'), (89, b'B+'), (85, b'B'), (80, b'B-'), (79, b'C+'), (75, b'C'), (70, b'C-'), (69, b'D+'), (65, b'D'), (60, b'D-'), (50, b'F'), (0, b'I'), (999, b'NA')]),
            preserve_default=True,
        ),
    ]
