# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Academic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_date', models.DateField(default=datetime.date.today)),
                ('test_level', models.IntegerField(default=0, choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('test_grade_math', models.IntegerField(max_length=3, null=True, blank=True)),
                ('test_grade_khmer', models.IntegerField(max_length=3, null=True, blank=True)),
                ('promote', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, verbose_name=b'Attendance Day')),
                ('attendance', models.CharField(default=b'P', max_length=2, null=True, choices=[(b'P', b'Present'), (b'UA', b'Unapproved Absence'), (b'AA', b'Approved Absence')])),
                ('notes', models.CharField(max_length=256, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttendanceDayOffering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('offered', models.CharField(default=b'Y', max_length=2, choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('classroom_id', models.AutoField(serialize=False, primary_key=True)),
                ('cohort', models.IntegerField(default=2014, max_length=8, verbose_name=b'Target Grade', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('classroom_number', models.CharField(max_length=16, verbose_name=b'Description', blank=True)),
                ('classroom_location', models.CharField(max_length=128, verbose_name=b'Classroom Location', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassroomEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enrollment_date', models.DateField(default=datetime.date.today)),
                ('drop_date', models.DateField(null=True, blank=True)),
                ('classroom_id', models.ForeignKey(to='mande.Classroom')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassroomTeacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classroom_id', models.ForeignKey(to='mande.Classroom')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('incident_date', models.DateField(default=datetime.date.today, verbose_name=b'Incident Date')),
                ('incident_code', models.IntegerField(default=1, choices=[(1, b'Bullying'), (2, b'Cheating'), (3, b'Lying'), (4, b'Cursing'), (5, b'Other')])),
                ('incident_description', models.CharField(default=b'', max_length=256)),
                ('classroom_id', models.ForeignKey(to='mande.Classroom')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExitSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('survey_date', models.DateField(default=datetime.date.today, verbose_name=b'Exit Survey Performed')),
                ('exit_date', models.DateField(verbose_name=b'Exit Date')),
                ('early_exit', models.CharField(default=b'NA', max_length=2, verbose_name=b'Early Exit (before achieveing age appropriate level)', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('last_grade', models.IntegerField(default=1, verbose_name=b'Public School Grade at exit', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('early_exit_reason', models.CharField(max_length=32, verbose_name=b'Reason for Leaving Early', choices=[(b'MOVING', b'Moving to another location'), (b'MOTIVATION', b"Don't want to continue."), (b'EMPLOYMENT', b'Got a job'), (b'OTHER', b'Other')])),
                ('early_exit_comment', models.TextField(verbose_name=b'Comment', blank=True)),
                ('secondary_enrollment', models.CharField(default=b'NA', max_length=2, verbose_name=b'Plan to enroll in secondary school?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Health',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appointment_date', models.DateField(default=datetime.date.today)),
                ('appointment_type', models.CharField(default=b'Check-up', max_length=16, choices=[(b'DENTAL', b'Dental'), (b'CHECKUP', b'Check-up')])),
                ('height', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('weight', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('extractions', models.IntegerField(default=0, max_length=1, null=True, blank=True)),
                ('sealent', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('filling', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('endo', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('scaling', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('pulped', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('xray', models.IntegerField(default=0, max_length=2, null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntakeInternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enrollment_date', models.DateField(verbose_name=b'Enrollment Date')),
                ('starting_grade', models.IntegerField(default=1, choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntakeSurvey',
            fields=[
                ('student_id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField(verbose_name=b'Date of Intake')),
                ('name', models.CharField(default=b'', max_length=64, verbose_name=b'Name')),
                ('dob', models.DateField(verbose_name=b'DOB')),
                ('grade_appropriate', models.IntegerField(default=1, verbose_name=b'Appropriate Grade', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('gender', models.CharField(default=b'M', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('address', models.TextField(verbose_name=b'Home Address')),
                ('enrolled', models.CharField(default=b'N', max_length=2, verbose_name=b'Currently enrolled in (public) school?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=-1, verbose_name=b'Current grade in [public] school (if enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('grade_last', models.IntegerField(default=-1, verbose_name=b'Last grade attended (if not enrolled)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('reasons', models.TextField(verbose_name=b'Reasons for not attening', blank=True)),
                ('father_name', models.CharField(max_length=64, verbose_name=b"Father's Name")),
                ('father_phone', models.CharField(max_length=128, verbose_name=b"Father's Phone")),
                ('father_profession', models.CharField(max_length=64, verbose_name=b"Father's Profession")),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_name', models.CharField(max_length=64, verbose_name=b"Mother's Name")),
                ('mother_phone', models.CharField(max_length=128, verbose_name=b"Mother's Phone")),
                ('mother_profession', models.CharField(max_length=64, verbose_name=b"Mother's Profession")),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0, verbose_name=b'Number of children living in household (including student)')),
                ('minors_in_school', models.IntegerField(default=0, verbose_name=b'Number of children enrolled in school last year')),
                ('minors_working', models.IntegerField(default=0, verbose_name=b'Number of children under 18 working 15+ hours per week')),
                ('minors_profession', models.CharField(max_length=256, verbose_name=b'What are they doing for work?', blank=True)),
                ('minors_encouraged', models.CharField(max_length=2, verbose_name=b'Did you encourage them to take this job?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training', models.CharField(max_length=2, verbose_name=b'Did they receive any vocational training?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training_type', models.CharField(max_length=256, verbose_name=b'What kind of vocational training did they receive?', blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntakeUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'Date of Update')),
                ('address', models.TextField(verbose_name=b'Home Address')),
                ('father_name', models.CharField(max_length=64, verbose_name=b"Father's Name", blank=True)),
                ('father_phone', models.CharField(max_length=128, verbose_name=b"Father's Phone", blank=True)),
                ('father_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Father's Profession", blank=True)),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_name', models.CharField(max_length=64, verbose_name=b"Mother's Name", blank=True)),
                ('mother_phone', models.CharField(max_length=128, verbose_name=b"Mother's Phone", blank=True)),
                ('mother_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Mother's Profession", blank=True)),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0)),
                ('minors_in_school', models.IntegerField(default=0)),
                ('minors_working', models.IntegerField(default=0)),
                ('minors_profession', models.CharField(default=b'NA', max_length=256, verbose_name=b'What are they doing for work?')),
                ('minors_encouraged', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did you encourage them to take this job?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did they receive any vocational training?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training_type', models.CharField(default=b'NA', max_length=256, verbose_name=b'What kind of vocational training did they receive?', blank=True)),
                ('enrolled', models.CharField(default=b'N', max_length=2, verbose_name=b'Currently enrolled in formal school?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=1, verbose_name=b'Current grade in (public) school?', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('grade_last', models.IntegerField(default=1, choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('reasons', models.TextField(default=b'NA')),
                ('notes', models.TextField(default=b'NA', blank=True)),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('user_generated', models.BooleanField(default=True)),
                ('text', models.TextField()),
                ('font_awesome_icon', models.TextField(default=b'fa-bolt', max_length=16)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostExitSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_exit_survey_date', models.DateField(default=datetime.date.today, verbose_name=b'Date of Survey')),
                ('exit_date', models.DateField(verbose_name=b'Exit Date')),
                ('early_exit', models.CharField(default=b'NA', max_length=2, verbose_name=b'Early (before achieving grade level) Exit', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('father_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Father's Profession")),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Mother's Profession")),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0, verbose_name=b'How many children (under 18) are working?')),
                ('enrolled', models.CharField(default=b'NA', max_length=2, verbose_name=b'Currently in school? [Primary Child]', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=1, verbose_name=b'Current Grade in formal school (if in school)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('grade_previous', models.IntegerField(default=1, verbose_name=b'Last Grade attended (if not in school)', choices=[(-1, b'Not Applicable'), (0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6'), (7, b'Grade 7'), (8, b'Grade 8'), (9, b'Grade 9'), (10, b'Grade 10'), (11, b'Grade 11'), (12, b'Grade 12'), (50, b'English'), (60, b'Computers'), (70, b'Vietnamese')])),
                ('reasons', models.TextField(verbose_name=b'Reasons for not attending', blank=True)),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('school_id', models.AutoField(serialize=False, primary_key=True)),
                ('school_name', models.CharField(max_length=128, verbose_name=b'School Code')),
                ('school_location', models.CharField(max_length=128, verbose_name=b'Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpiritualActivitiesSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name=b'Survey Date')),
                ('family_attend_church', models.CharField(default=b'NA', max_length=2, verbose_name=b'Does your family currently attend church?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('personal_attend_church', models.CharField(default=b'NA', max_length=2, verbose_name=b'Do you currently attend church?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('personal_prayer', models.CharField(default=b'NA', max_length=2, verbose_name=b'Have you prayed on your own within the last week?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('personal_baptism', models.CharField(default=b'NA', max_length=2, verbose_name=b'Have you been baptized?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('personal_bible_reading', models.CharField(default=b'NA', max_length=2, verbose_name=b'Have you spent time reading the Bible in the last week?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('personal_prayer_aloud', models.CharField(default=b'NA', max_length=2, verbose_name=b'Have you prayed aloud in the last week?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name=b'Observation Date')),
                ('academic_score', models.IntegerField(verbose_name=b'Academic Growth Score')),
                ('study_score', models.IntegerField(verbose_name=b'Study/Learning Skills Score')),
                ('personal_score', models.IntegerField(verbose_name=b'Life Skills/Personal Development Score')),
                ('hygiene_score', models.IntegerField(verbose_name=b'Hygeine Score')),
                ('faith_score', models.IntegerField(verbose_name=b'Christian Growth Score')),
                ('comments', models.TextField(verbose_name=b'Overall comments', blank=True)),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacher_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='intakesurvey',
            name='site',
            field=models.ForeignKey(to='mande.School'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='intakeinternal',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey', unique=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='health',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exitsurvey',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discipline',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classroomteacher',
            name='teacher_id',
            field=models.ForeignKey(to='mande.Teacher'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classroomenrollment',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='classroomenrollment',
            unique_together=set([('student_id', 'classroom_id')]),
        ),
        migrations.AddField(
            model_name='classroom',
            name='school_id',
            field=models.ForeignKey(to='mande.School'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendancedayoffering',
            name='classroom_id',
            field=models.ForeignKey(to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('student_id', 'date')]),
        ),
        migrations.AddField(
            model_name='academic',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='academic',
            unique_together=set([('student_id', 'test_date', 'test_level', 'promote')]),
        ),
    ]
