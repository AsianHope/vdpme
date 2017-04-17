# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0031_auto_20161215_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='spiritualactivitiessurvey',
            name='church_name',
            field=models.CharField(max_length=128, null=True, verbose_name='Church name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='spiritualactivitiessurvey',
            name='frequency_of_attending',
            field=models.CharField(default=b'NA', max_length=16, choices=[(b'NA', 'Not Applicable'), (b'EVERY_WEEK', 'Almost every week'), (b'EVERY_MONTH', 'Once every 1-2 months'), (b'EVERY_YEAR', 'Once or twice per year')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spiritualactivitiessurvey',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Survey Date'),
            preserve_default=True,
        ),
    ]
