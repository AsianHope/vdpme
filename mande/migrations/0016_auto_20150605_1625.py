# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0015_auto_20150605_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_employment',
            field=models.CharField(default=1, max_length=1, verbose_name=b"Guardian 1's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_name',
            field=models.CharField(max_length=64, verbose_name=b"Guardian 1's Name"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_phone',
            field=models.CharField(max_length=128, verbose_name=b"Guardian 1's Phone"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_profession',
            field=models.CharField(max_length=64, verbose_name=b"Guardian 1's Profession"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_employment',
            field=models.CharField(default=1, choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')], max_length=1, blank=True, null=True, verbose_name=b"Guardian 2's Employment"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_name',
            field=models.CharField(max_length=64, null=True, verbose_name=b"Guardian 2's Name", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_phone',
            field=models.CharField(max_length=128, null=True, verbose_name=b"Guardian 2's Phone", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_profession',
            field=models.CharField(default=b'NA', max_length=64, null=True, verbose_name=b"Guardian 2's Profession", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_employment',
            field=models.CharField(default=1, max_length=1, verbose_name=b"Guardian 1's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_name',
            field=models.CharField(max_length=64, verbose_name=b"Guardian 1's Name", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_phone',
            field=models.CharField(max_length=128, verbose_name=b"Guardian 1's Phone", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_profession',
            field=models.CharField(default=b'NA', max_length=64, verbose_name=b"Guardian 1's Profession", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_employment',
            field=models.CharField(default=1, choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')], max_length=1, blank=True, null=True, verbose_name=b"Guardian 2's Employment"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_name',
            field=models.CharField(max_length=64, null=True, verbose_name=b"Guardian 2's Name", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_phone',
            field=models.CharField(max_length=128, null=True, verbose_name=b"Guardian 2's Phone", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_profession',
            field=models.CharField(default=b'NA', max_length=64, null=True, verbose_name=b"Guardian 2's Profession", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='guardian1_relationship',
            field=models.CharField(default=b'FATHER', max_length=64, verbose_name=b"Guardian 1's relationship to child", choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='guardian2_relationship',
            field=models.CharField(default=b'MOTHER', choices=[(b'FATHER', b'Father'), (b'MOTHER', b'Mother'), (b'GRANDFATHER', b'Grandfather'), (b'GRANDMOTHER', b'Grandmother'), (b'AUNT', b'Aunt'), (b'UNCLE', b'Uncle'), (b'OTHER', b'Other')], max_length=64, blank=True, null=True, verbose_name=b"Guardian 2's relationship to child"),
            preserve_default=True,
        ),
    ]
