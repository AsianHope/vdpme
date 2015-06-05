# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0012_attendance_classroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intakesurvey',
            name='reasons',
            field=models.TextField(verbose_name=b'Reasons for not attending', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='health',
            unique_together=set([('student_id', 'appointment_date', 'appointment_type')]),
        ),
    ]
