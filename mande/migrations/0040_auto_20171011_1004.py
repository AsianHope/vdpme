# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-11 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0039_auto_20170914_1515'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jethroperms',
            options={'permissions': (('view_academic_select', 'Can view academic_select'), ('view_evaluation_making_period', 'Can view evaluation_making_per'), ('view_student_lag_report', 'Can view student_lag_report'), ('view_discipline_form', 'Can view discipline_form'), ('view_academic_making_period', 'Can view academic_making_perio'), ('view_classroomenrollment_form', 'Can view classroomenrollment_f'), ('view_take_class_attendance', 'Can view take_class_attendance'), ('view_attendance', 'Can view attendance'), ('view_notification_log', 'Can view notification_log'), ('view_save_photo', 'Can view save_photo'), ('view_publicschool_form', 'Can view publicschool_form'), ('view_daily_absence_report', 'Can view daily_absence_report'), ('view_mande_summary_report', 'Can view mande_summary_report'), ('view_exit_survey', 'Can view exit_survey'), ('view_anomalous_data', 'Can view anomalous_data'), ('view_attendance_days', 'Can view attendance_days'), ('view_classroomenrollment_individual', 'Can view classroomenrollment_i'), ('view_student_medical_report', 'Can view student_medical_repor'), ('view_exit_surveys_list', 'Can view exit_surveys_list'), ('view_delete_public_school', 'Can view delete_public_school'), ('view_delete_spiritualactivities_survey', 'Can view delete_spiritualactiv'), ('view_teacher_form', 'Can view teacher_form'), ('view_student_attendance_detail', 'Can view student_attendance_de'), ('view_dashboard', 'Can view dashboard'), ('view_post_exit_survey', 'Can view post_exit_survey'), ('view_studentevaluation_form', 'Can view studentevaluation_for'), ('view_classroom_form', 'Can view classroom_form'), ('view_health_form', 'Can view health_form'), ('view_advanced_report', 'Can view advanced_report'), ('view_studentevaluation_form_single', 'Can view studentevaluation_for'), ('view_intake_internal', 'Can view intake_internal'), ('view_attendance_summary_report', 'Can view attendance_summary_re'), ('view_student_dental_report', 'Can view student_dental_report'), ('view_intake_update', 'Can view intake_update'), ('view_student_detail', 'Can view student_detail'), ('view_intake_survey', 'Can view intake_survey'), ('view_take_attendance', 'Can view take_attendance'), ('view_classroomteacher_form', 'Can view classroomteacher_form'), ('view_class_list', 'Can view class_list'), ('view_academic_form', 'Can view academic_form'), ('view_post_exit_survey_list', 'Can view post_exit_survey_list'), ('view_public_school_report', 'Can view public_school_report'), ('view_unapproved_absence_with_no_comment', 'Can view unapproved_absence_wi'), ('view_student_absence_report', 'Can view student_absence_repor'), ('view_student_evaluation_report', 'Can view student_evaluation_re'), ('view_academic_form_single', 'Can view academic_form_single'), ('view_students_lag_summary', 'Can view students_lag_summary'), ('view_data_audit', 'Can view data_audit'), ('view_update_current_grade', 'Can view update_current_grade'), ('view_studentevaluation_select', 'Can view studentevaluation_sel'), ('view_generate', 'Can view generate'), ('view_daily_attendance_report', 'Can view daily_attendance_repo'), ('view_spiritualactivities_survey', 'Can view spiritualactivities_s'), ('view_attendance_calendar', 'Can view attendance_calendar'), ('view_students_intergrated_in_public_school', 'Can view students_intergrated_'), ('view_student_promoted_report', 'Can view student_promoted_repo'), ('view_students_promoted_times_report', 'Can view students_promoted_tim'), ('view_student_dental_summary_report', 'Can view student_dental_summar'), ('view_student_list', 'Can view student_list'), ('view_student_achievement_test_report', 'Can view student_achievement_t'))},
        ),
        migrations.AddField(
            model_name='intakeupdate',
            name='current_grade',
            field=models.IntegerField(blank=True, choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], null=True, verbose_name='Current Grade'),
        ),
        migrations.AlterField(
            model_name='academic',
            name='test_level',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], default=0, verbose_name='Level'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='cohort',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Target Grade'),
        ),
        migrations.AlterField(
            model_name='currentstudentinfo',
            name='vdp_grade',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], verbose_name='VDP Grade'),
        ),
        migrations.AlterField(
            model_name='exitsurvey',
            name='last_grade',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Public School Grade at Exit'),
        ),
        migrations.AlterField(
            model_name='intakeinternal',
            name='starting_grade',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Starting Grade'),
        ),
        migrations.AlterField(
            model_name='intakesurvey',
            name='grade_appropriate',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'G1'), (2, 'G2'), (3, 'G3'), (4, 'G4'), (5, 'G5'), (6, 'G6'), (51, 'E1'), (52, 'E2'), (53, 'E3'), (54, 'E4'), (55, 'E5'), (60, 'Computers'), (71, 'V1'), (72, 'V2'), (73, 'V3'), (74, 'V4'), (75, 'V5'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Appropriate Grade'),
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='grade_current',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Current Grade in formal school (if in school)'),
        ),
        migrations.AlterField(
            model_name='postexitsurvey',
            name='grade_previous',
            field=models.IntegerField(choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (999, 'No Grade / Never Studied')], default=1, verbose_name='Last Grade attended (if not in school)'),
        ),
        migrations.AlterField(
            model_name='publicschoolhistory',
            name='grade',
            field=models.IntegerField(blank=True, choices=[(-1, 'Not Applicable'), (0, 'Not Enrolled'), (1, 'Grade 1'), (2, 'Grade 2'), (3, 'Grade 3'), (4, 'Grade 4'), (5, 'Grade 5'), (6, 'Grade 6'), (7, 'Grade 7'), (8, 'Grade 8'), (9, 'Grade 9'), (10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12'), (999, 'No Grade / Never Studied')], null=True, verbose_name='Grade'),
        ),
    ]
