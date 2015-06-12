# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0018_auto_20150608_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='minors_in_public_school',
            field=models.IntegerField(default=0, verbose_name=b'Number of children enrolled in public school last year'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='reasons',
            field=models.TextField(default=b'NA', null=True, verbose_name=b'Reasons for not attending school', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other'), (b'NONE', b'No guardian')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='academic_score',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Academic Growth Score', choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='faith_score',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Christian Growth Score', choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='hygiene_score',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Hygeine Knowledge Score', choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='personal_score',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Life Skills/Personal Development Score', choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='study_score',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Study/Learning Skills Score', choices=[(1, b'1 - Little to no Growth'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5 - Huge Growth')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='studentevaluation',
            unique_together=set([('student_id', 'date')]),
        ),
    ]
