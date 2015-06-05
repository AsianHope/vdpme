# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0013_auto_20150603_1325'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postexitsurvey',
            old_name='father_employment',
            new_name='guardian1_employment'
        ),
        migrations.RenameField(
            model_name='postexitsurvey',
            old_name='father_profession',
            new_name='guardian1_profession'
        ),
        migrations.RenameField(
            model_name='postexitsurvey',
            old_name='mother_employment',
            new_name='guardian2_employment'
        ),
        migrations.RenameField(
            model_name='postexitsurvey',
            old_name='mother_profession',
            new_name='guardian2_profession'
        ),
        migrations.AddField(
            model_name='postexitsurvey',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'MOTHER', b'Mother'), (b'FATHER', b'Father'), (b'GRANDMOTHER', b'Grandmother'), (b'GRANDFATHER', b'Grandfather'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='postexitsurvey',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'MOTHER', b'Mother'), (b'FATHER', b'Father'), (b'GRANDMOTHER', b'Grandmother'), (b'GRANDFATHER', b'Grandfather'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
    ]
