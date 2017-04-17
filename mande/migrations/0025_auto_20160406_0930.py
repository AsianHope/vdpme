# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0024_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academic',
            name='test_level',
            field=models.IntegerField(default=0, choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='cohort',
            field=models.IntegerField(default=2014, verbose_name=b'Target Grade', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='exitsurvey',
            name='last_grade',
            field=models.IntegerField(default=1, verbose_name=b'Public School Grade at exit', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeinternal',
            name='starting_grade',
            field=models.IntegerField(default=1, choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='grade_appropriate',
            field=models.IntegerField(default=1, verbose_name=b'Appropriate Grade', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='grade_current',
            field=models.IntegerField(default=-1, verbose_name=b'Current grade in [public] school (if enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='grade_last',
            field=models.IntegerField(default=-1, verbose_name=b'Last grade attended (if not enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='grade_current',
            field=models.IntegerField(default=1, verbose_name=b'Current grade in (public) school?', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='grade_last',
            field=models.IntegerField(default=b'-1', verbose_name=b'Last grade in public school (if not currently enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='grade_current',
            field=models.IntegerField(default=1, verbose_name=b'Current Grade in formal school (if in school)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='grade_previous',
            field=models.IntegerField(default=1, verbose_name=b'Last Grade attended (if not in school)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese'), (999, b'No Grade / Never Studied')]),
            preserve_default=True,
        ),
    ]
