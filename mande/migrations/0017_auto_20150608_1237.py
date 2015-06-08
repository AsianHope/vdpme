# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0016_auto_20150605_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='intakesurvey',
            name='minors_in_other_school',
            field=models.IntegerField(default=0, verbose_name=b'Number of children enrolled in private school last year'),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='intakesurvey',
	    old_name='minors_in_school',
            new_name='minors_in_public_school',
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='grade_last',
            field=models.IntegerField(default=b'-1', verbose_name=b'Last grade in public school (if not currently enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='minors',
            field=models.IntegerField(default=0, verbose_name=b'Number of children living in household (including student)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='minors_in_school',
            field=models.IntegerField(default=0, verbose_name=b'Number of children enrolled in school last year'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='minors_working',
            field=models.IntegerField(default=0, verbose_name=b'Number of minors working'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='reasons',
            field=models.TextField(default=b'NA', verbose_name=b'Reasons for not attending school'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='minors',
            field=models.IntegerField(default=0, verbose_name=b'How many children in the household?'),
            preserve_default=True,
        ),
    ]
