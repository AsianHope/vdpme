# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0017_auto_20150608_1237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intakeupdate',
            old_name='minors_in_school',
            new_name='minors_in_public_school',
        ),
        migrations.AddField(
            model_name='intakeupdate',
            name='minors_in_other_school',
            field=models.IntegerField(default=0, verbose_name=b'Number of children enrolled in private school last year'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='minors_in_public_school',
            field=models.IntegerField(default=0, verbose_name=b'Number of children enrolled in public school last year'),
            preserve_default=True,
        ),
    ]
