# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0030_auto_20161214_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academic',
            name='promote',
            field=models.BooleanField(default=False, verbose_name='Promote'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Test Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_grade_khmer',
            field=models.IntegerField(null=True, verbose_name='Khmer', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_grade_math',
            field=models.IntegerField(null=True, verbose_name='Math', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_level',
            field=models.IntegerField(default=0, verbose_name='Level', choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (50, 'English'), (60, 'Computers'), (70, 'Vietnamese'), (999, 'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='attendance',
            field=models.CharField(default=b'P', max_length=2, null=True, verbose_name='Attendance', choices=[(b'P', 'Present'), (b'UA', 'Unapproved Absence'), (b'AA', 'Approved Absence')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='classroom',
            field=models.ForeignKey(verbose_name='Classroom', blank=True, to='mande.Classroom', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='notes',
            field=models.CharField(max_length=256, verbose_name='Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancedayoffering',
            name='classroom_id',
            field=models.ForeignKey(verbose_name='Classroom ID', to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancedayoffering',
            name='date',
            field=models.DateField(verbose_name='Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancedayoffering',
            name='offered',
            field=models.CharField(default=b'Y', max_length=2, verbose_name='Offered', choices=[(b'Y', 'Yes'), (b'N', 'No'), (b'NA', 'Not Applicable')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='absent',
            field=models.IntegerField(default=0, verbose_name='Absent'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='classroom',
            field=models.ForeignKey(verbose_name='Classroom ID', to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='date',
            field=models.DateField(verbose_name='Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='attendancelog',
            name='present',
            field=models.IntegerField(default=0, verbose_name='Present'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='attendance_calendar',
            field=models.ForeignKey(default=None, blank=True, to='mande.Classroom', null=True, verbose_name='Attendance calendar'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='classroom_id',
            field=models.AutoField(serialize=False, verbose_name='Classroom ID', primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroom',
            name='school_id',
            field=models.ForeignKey(verbose_name='School ID', to='mande.School'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomenrollment',
            name='classroom_id',
            field=models.ForeignKey(verbose_name='Classroom ID', to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomenrollment',
            name='drop_date',
            field=models.DateField(null=True, verbose_name='Drop Date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomenrollment',
            name='enrollment_date',
            field=models.DateField(default=datetime.date.today, verbose_name=b'Enrollment Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomenrollment',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomteacher',
            name='classroom_id',
            field=models.ForeignKey(verbose_name='Classroom ID', to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='classroomteacher',
            name='teacher_id',
            field=models.ForeignKey(verbose_name='Teacher ID', to='mande.Teacher'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='discipline',
            name='classroom_id',
            field=models.ForeignKey(verbose_name='Classroom ID', to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='discipline',
            name='incident_code',
            field=models.IntegerField(default=1, verbose_name='Incident code', choices=[(1, 'Bullying'), (2, 'Cheating'), (3, 'Lying'), (4, 'Cursing'), (5, 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='discipline',
            name='incident_description',
            field=models.CharField(default=b'', max_length=256, verbose_name='Incident description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='discipline',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeinternal',
            name='starting_grade',
            field=models.IntegerField(default=1, verbose_name='Starting grade', choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (50, 'English'), (60, 'Computers'), (70, 'Vietnamese'), (999, 'No Grade / Never Studied')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeinternal',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='notes',
            field=models.TextField(default=b'NA', verbose_name=b'Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakeupdate',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='date',
            field=models.DateTimeField(auto_now=True, verbose_name='Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='font_awesome_icon',
            field=models.TextField(default=b'fa-bolt', max_length=16, verbose_name=b'Font Awesome Icon'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='text',
            field=models.TextField(verbose_name='Text'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='user',
            field=models.ForeignKey(verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='user_generated',
            field=models.BooleanField(default=True, verbose_name='User Generated'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='academic_year',
            field=models.IntegerField(verbose_name='Academic Year', choices=[(2014, b'2014-2015'), (2015, b'2015-2016'), (2016, b'2016-2017'), (2017, b'2017-2018'), (2018, b'2018-2019'), (2019, b'2019-2020'), (2020, b'2020-2021'), (2021, b'2021-2022'), (2022, b'2022-2023'), (2023, b'2023-2024'), (2024, b'2024-2025')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='drop_date',
            field=models.DateField(null=True, verbose_name='Drop Date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='enroll_date',
            field=models.DateField(null=True, verbose_name='Enroll Date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='status',
            field=models.CharField(default=b'COMPLETED', max_length=16, verbose_name='Status', choices=[(b'COMPLETED', 'Completed'), (b'DROPPED', 'Dropped out'), (b'ON_GOING', 'On going')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='school',
            name='school_id',
            field=models.AutoField(serialize=False, verbose_name='School ID', primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='comments',
            field=models.TextField(verbose_name='Overall Comments', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='hygiene_score',
            field=models.IntegerField(default=None, null=True, verbose_name='Hygiene Knowledge Score', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentevaluation',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='name',
            field=models.CharField(default=b'', unique=True, max_length=32, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='teacher_id',
            field=models.AutoField(serialize=False, verbose_name='Teacher ID', primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='publicschoolhistory',
            unique_together=set([('student_id', 'grade', 'academic_year', 'status')]),
        ),
    ]
