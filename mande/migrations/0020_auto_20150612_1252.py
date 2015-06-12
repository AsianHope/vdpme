# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0019_auto_20150612_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentevaluation',
            name='academic_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Academic Growth Score', blank=True, choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='faith_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Christian Growth Score', blank=True, choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='hygiene_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Hygeine Knowledge Score', blank=True, choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='personal_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Life Skills/Personal Development Score', blank=True, choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='study_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Study/Learning Skills Score', blank=True, choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
    ]
