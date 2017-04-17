# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0034_auto_20170403_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spiritualactivitiessurvey',
            name='frequency_of_attending',
            field=models.CharField(blank=True, max_length=16, verbose_name='Frequency of Attending', choices=[(b'EVERY_WEEK', 'Almost every week'), (b'EVERY_MONTH', 'Once every 1-2 months'), (b'EVERY_YEAR', 'Once or twice per year')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spiritualactivitiessurvey',
            name='personal_attend_church',
            field=models.CharField(max_length=2, verbose_name='Did the student attend church within the past 6 months?', choices=[(b'Y', 'Yes'), (b'N', 'No')]),
            preserve_default=True,
        ),
    ]
