# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0028_auto_20160822_1608'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jethroperms',
            options={'permissions': (('view_academic_select', 'Can view academic_select'), ('view_student_lag_report', 'Can view student_lag_report'), ('view_discipline_form', 'Can view discipline_form'), ('view_classroomenrollment_form', 'Can view classroomenrollment_f'), ('view_take_class_attendance', 'Can view take_class_attendance'), ('view_attendance', 'Can view attendance'), ('view_notification_log', 'Can view notification_log'), ('view_daily_absence_report', 'Can view daily_absence_report'), ('view_mande_summary_report', 'Can view mande_summary_report'), ('view_exit_survey', 'Can view exit_survey'), ('view_take_attendance', 'Can view take_attendance'), ('view_attendance_days', 'Can view attendance_days'), ('view_classroomenrollment_individual', 'Can view classroomenrollment_i'), ('view_exit_surveys_list', 'Can view exit_surveys_list'), ('view_student_medical_report', 'Can view student_medical_repor'), ('view_teacher_form', 'Can view teacher_form'), ('view_student_attendance_detail', 'Can view student_attendance_de'), ('view_dashboard', 'Can view dashboard'), ('view_studentevaluation_form', 'Can view studentevaluation_for'), ('view_classroom_form', 'Can view classroom_form'), ('view_health_form', 'Can view health_form'), ('view_advanced_report', 'Can view advanced_report'), ('view_studentevaluation_form_single', 'Can view studentevaluation_for'), ('view_intake_internal', 'Can view intake_internal'), ('view_attendance_summary_report', 'Can view attendance_summary_re'), ('view_student_dental_report', 'Can view student_dental_report'), ('view_intake_update', 'Can view intake_update'), ('view_student_detail', 'Can view student_detail'), ('view_intake_survey', 'Can view intake_survey'), ('view_post_exit_survey', 'Can view post_exit_survey'), ('view_classroomteacher_form', 'Can view classroomteacher_form'), ('view_class_list', 'Can view class_list'), ('view_academic_form', 'Can view academic_form'), ('view_post_exit_survey_list', 'Can view post_exit_survey_list'), ('view_student_absence_report', 'Can view student_absence_repor'), ('view_student_evaluation_report', 'Can view student_evaluation_re'), ('view_academic_form_single', 'Can view academic_form_single'), ('view_anomolous_data', 'Can view anomolous_data'), ('view_students_lag_summary', 'Can view students_lag_summary'), ('view_data_audit', 'Can view data_audit'), ('view_studentevaluation_select', 'Can view studentevaluation_sel'), ('view_daily_attendance_report', 'Can view daily_attendance_repo'), ('view_spiritualactivities_survey', 'Can view spiritualactivities_s'), ('view_attendance_calendar', 'Can view attendance_calendar'), ('view_students_intergrated_in_public_school', 'Can view students_intergrated_'), ('view_students_not_enrolled_in_public_school_report', 'Can view students_not_enrolled'), ('view_student_promoted_report', 'Can view student_promoted_repo'), ('view_students_promoted_times_report', 'Can view students_promoted_tim'), ('view_student_dental_summary_report', 'Can view student_dental_summar'), ('view_student_list', 'Can view student_list'), ('view_student_achievement_test_report', 'Can view student_achievement_t'))},
        ),
        migrations.AddField(
            model_name='classroom',
            name='attendance_calendar',
            field=models.ForeignKey(default=None, blank=True, to='mande.Classroom', null=True),
            preserve_default=True,
        ),
    ]
