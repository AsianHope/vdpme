# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0020_auto_20150612_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentevaluation',
            name='academic_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Academic Growth Score', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='faith_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Christian Growth Score', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='hygiene_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Hygeine Knowledge Score', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='personal_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Life Skills/Personal Development Score', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='study_score',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Study/Learning Skills Score', blank=True),
            preserve_default=True,
        ),
    ]
