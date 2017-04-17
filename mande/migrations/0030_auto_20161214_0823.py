# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0029_auto_20160921_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicSchoolHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('academic_year', models.IntegerField(choices=[(2014, b'2014-2015'), (2015, b'2015-2016'), (2016, b'2016-2017'), (2017, b'2017-2018'), (2018, b'2018-2019'), (2019, b'2019-2020'), (2020, b'2020-2021'), (2021, b'2021-2022'), (2022, b'2022-2023'), (2023, b'2023-2024'), (2024, b'2024-2025')])),
                ('grade', models.IntegerField(verbose_name=b'Public School Grade', choices=[(1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12')])),
                ('status', models.CharField(default=b'COMPLETED', max_length=16, choices=[(b'COMPLETED', b'Completed'), (b'DROPPED', b'Dropped out'), (b'ON_GOING', b'On going')])),
                ('enroll_date', models.DateField(null=True, blank=True)),
                ('drop_date', models.DateField(null=True, blank=True)),
                ('school_name', models.CharField(max_length=128, verbose_name=b'Public School Name', blank=True)),
                ('reasons', models.TextField(verbose_name=b'Reasons for not attending', blank=True)),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='publicschoolhistory',
            unique_together=set([('student_id', 'grade')]),
        ),
        migrations.AlterModelOptions(
            name='jethroperms',
            options={'permissions': (('view_academic_select', 'Can view academic_select'), ('view_student_lag_report', 'Can view student_lag_report'), ('view_discipline_form', 'Can view discipline_form'), ('view_classroomenrollment_form', 'Can view classroomenrollment_f'), ('view_take_class_attendance', 'Can view take_class_attendance'), ('view_attendance', 'Can view attendance'), ('view_notification_log', 'Can view notification_log'), ('view_publicschool_form', 'Can view publicschool_form'), ('view_daily_absence_report', 'Can view daily_absence_report'), ('view_mande_summary_report', 'Can view mande_summary_report'), ('view_exit_survey', 'Can view exit_survey'), ('view_take_attendance', 'Can view take_attendance'), ('view_anomalous_data', 'Can view anomalous_data'), ('view_attendance_days', 'Can view attendance_days'), ('view_classroomenrollment_individual', 'Can view classroomenrollment_i'), ('view_exit_surveys_list', 'Can view exit_surveys_list'), ('view_student_medical_report', 'Can view student_medical_repor'), ('view_teacher_form', 'Can view teacher_form'), ('view_student_attendance_detail', 'Can view student_attendance_de'), ('view_dashboard', 'Can view dashboard'), ('view_studentevaluation_form', 'Can view studentevaluation_for'), ('view_classroom_form', 'Can view classroom_form'), ('view_health_form', 'Can view health_form'), ('view_advanced_report', 'Can view advanced_report'), ('view_studentevaluation_form_single', 'Can view studentevaluation_for'), ('view_intake_internal', 'Can view intake_internal'), ('view_attendance_summary_report', 'Can view attendance_summary_re'), ('view_student_dental_report', 'Can view student_dental_report'), ('view_intake_update', 'Can view intake_update'), ('view_student_detail', 'Can view student_detail'), ('view_intake_survey', 'Can view intake_survey'), ('view_post_exit_survey', 'Can view post_exit_survey'), ('view_classroomteacher_form', 'Can view classroomteacher_form'), ('view_class_list', 'Can view class_list'), ('view_academic_form', 'Can view academic_form'), ('view_post_exit_survey_list', 'Can view post_exit_survey_list'), ('view_public_school_report', 'Can view public_school_report'), ('view_unapproved_absence_with_no_comment', 'Can view unapproved_absence_wi'), ('view_student_absence_report', 'Can view student_absence_repor'), ('view_student_evaluation_report', 'Can view student_evaluation_re'), ('view_academic_form_single', 'Can view academic_form_single'), ('view_students_lag_summary', 'Can view students_lag_summary'), ('view_data_audit', 'Can view data_audit'), ('view_studentevaluation_select', 'Can view studentevaluation_sel'), ('view_daily_attendance_report', 'Can view daily_attendance_repo'), ('view_spiritualactivities_survey', 'Can view spiritualactivities_s'), ('view_attendance_calendar', 'Can view attendance_calendar'), ('view_students_intergrated_in_public_school', 'Can view students_intergrated_'), ('view_student_promoted_report', 'Can view student_promoted_repo'), ('view_students_promoted_times_report', 'Can view students_promoted_tim'), ('view_student_dental_summary_report', 'Can view student_dental_summar'), ('view_student_list', 'Can view student_list'), ('view_student_achievement_test_report', 'Can view student_achievement_t'))},
        ),
        migrations.AddField(
            model_name='intakesurvey',
            name='public_school_name',
            field=models.CharField(max_length=128, verbose_name='Public School Name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intakeupdate',
            name='public_school_name',
            field=models.CharField(max_length=128, verbose_name=b'Public School Name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='teacher',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='exitsurvey',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='appointment_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Appointment date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='appointment_type',
            field=models.CharField(default=b'Check-up', max_length=16, verbose_name='Appointment type', choices=[(b'DENTAL', 'Dental'), (b'CHECKUP', 'Check-up')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='endo',
            field=models.IntegerField(default=0, null=True, verbose_name='Endo', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='extractions',
            field=models.IntegerField(default=0, null=True, verbose_name='Extractions', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='filling',
            field=models.IntegerField(default=0, null=True, verbose_name='Filling', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='height',
            field=models.DecimalField(null=True, verbose_name='Height', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='notes',
            field=models.TextField(verbose_name='Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='pulped',
            field=models.IntegerField(default=0, null=True, verbose_name='Pulped', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='scaling',
            field=models.IntegerField(default=0, null=True, verbose_name='Scaling', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='sealent',
            field=models.IntegerField(default=0, null=True, verbose_name='Sealent', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='weight',
            field=models.DecimalField(null=True, verbose_name='Weight', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='health',
            name='xray',
            field=models.IntegerField(default=0, null=True, verbose_name='Xray', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='gender',
            field=models.CharField(default=b'M', max_length=1, verbose_name='Gender', choices=[(b'M', 'Male'), (b'F', 'Female')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='notes',
            field=models.TextField(verbose_name='Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='site',
            field=models.ForeignKey(verbose_name='Site', to='mande.School'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='student_id',
            field=models.AutoField(serialize=False, verbose_name=b'Student ID', primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spiritualactivitiessurvey',
            name='student_id',
            field=models.ForeignKey(verbose_name='Student ID', to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='name',
            field=models.CharField(default=b'', unique=True, max_length=32),
            preserve_default=True,
        ),
    ]
