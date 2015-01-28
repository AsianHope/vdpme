# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Academic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_date', models.DateField(default=datetime.date.today)),
                ('test_level', models.CharField(default=0, max_length=2, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('test_grade_math', models.IntegerField(default=70, max_length=3, choices=[(99, b'A+'), (95, b'A'), (90, b'A-'), (89, b'B+'), (85, b'B'), (80, b'B-'), (79, b'C+'), (75, b'C'), (70, b'C-'), (69, b'D+'), (65, b'D'), (60, b'D-'), (50, b'F'), (0, b'I'), (-1, b'NA')])),
                ('test_grade_khmer', models.IntegerField(default=70, max_length=3, choices=[(99, b'A+'), (95, b'A'), (90, b'A-'), (89, b'B+'), (85, b'B'), (80, b'B-'), (79, b'C+'), (75, b'C'), (70, b'C-'), (69, b'D+'), (65, b'D'), (60, b'D-'), (50, b'F'), (0, b'I'), (-1, b'NA')])),
                ('promote', models.CharField(default=b'NA', max_length=2, choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
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
                ('attendance', models.CharField(max_length=2, choices=[(b'P', b'Present'), (b'A', b'Unapproved Absence'), (b'AA', b'Approved Absence')])),
                ('notes', models.CharField(default=b'', max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttendanceDaysOffered',
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
                ('cohort', models.CharField(default=2014, max_length=8, verbose_name=b'Cohort', choices=[(2014, b'2014-2015'), (2015, b'2015-2016'), (2016, b'2016-2017'), (2017, b'2017-2018'), (2018, b'2018-2019'), (2019, b'2019-2020'), (2020, b'2020-2021'), (2021, b'2021-2022'), (2022, b'2022-2023'), (2023, b'2023-2024'), (2024, b'2024-2025')])),
                ('classroom_number', models.CharField(max_length=16, verbose_name=b'Classroom Number')),
                ('classroom_location', models.CharField(max_length=128, verbose_name=b'Classroom Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassroomEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('incident_date', models.DateTimeField(default=datetime.datetime.now)),
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
                ('exit_date', models.DateField(verbose_name=b'Exit Date')),
                ('early_exit', models.CharField(default=b'NA', max_length=2, verbose_name=b'Early (Pre 6th Grade) Exit', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('last_grade', models.IntegerField(default=1, max_length=1, verbose_name=b'Early (Pre 6th Grade) Exit', choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('early_exit_reason', models.TextField(default=b'NA', verbose_name=b'Reason Leaving Early')),
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
                ('height', models.DecimalField(max_digits=5, decimal_places=2)),
                ('weight', models.DecimalField(max_digits=5, decimal_places=2)),
                ('extractions', models.IntegerField(default=0, max_length=1)),
                ('sealent', models.CharField(default=b'NA', max_length=2, choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('filling', models.IntegerField(default=0, max_length=1)),
                ('endo', models.IntegerField(default=0, max_length=1)),
                ('scaling', models.IntegerField(default=0, max_length=1)),
                ('pulped', models.IntegerField(default=0, max_length=1)),
                ('xray', models.IntegerField(default=0, max_length=1)),
                ('notes', models.TextField(default=b'')),
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
                ('starting_grade', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntakeSurvey',
            fields=[
                ('student_id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'Date of Intake')),
                ('name', models.CharField(default=b'', max_length=64, verbose_name=b'Name')),
                ('dob', models.DateField(verbose_name=b'DOB')),
                ('grade_appropriate', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('graduation', models.IntegerField()),
                ('gender', models.CharField(default=b'M', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('address', models.TextField(verbose_name=b'Home Address')),
                ('father_name', models.CharField(max_length=64, verbose_name=b"Father's Name")),
                ('father_phone', models.CharField(max_length=64, verbose_name=b"Father's Phone")),
                ('father_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Father's Profession")),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_name', models.CharField(max_length=64, verbose_name=b"Mother's Name")),
                ('mother_phone', models.CharField(max_length=64, verbose_name=b"Mother's Phone")),
                ('mother_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Mother's Profession")),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0)),
                ('minors_in_school', models.IntegerField(default=0)),
                ('minors_working', models.IntegerField(default=0)),
                ('minors_profession', models.CharField(default=b'NA', max_length=256, verbose_name=b'What are they doing for work?')),
                ('minors_encouraged', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did you encourage them to take this job?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did they receive any vocational training?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training_type', models.CharField(default=b'NA', max_length=256, verbose_name=b'What kind of vocational training did they receive?')),
                ('enrolled', models.CharField(default=b'N', max_length=2, verbose_name=b'Currently enrolled?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('grade_last', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('reasons', models.TextField(default=b'NA')),
                ('notes', models.TextField(default=b'NA')),
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
                ('father_name', models.CharField(max_length=64, verbose_name=b"Father's Name")),
                ('father_phone', models.CharField(max_length=64, verbose_name=b"Father's Phone")),
                ('father_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Father's Profession")),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_name', models.CharField(max_length=64, verbose_name=b"Mother's Name")),
                ('mother_phone', models.CharField(max_length=64, verbose_name=b"Mother's Phone")),
                ('mother_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Mother's Profession")),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0)),
                ('minors_in_school', models.IntegerField(default=0)),
                ('minors_working', models.IntegerField(default=0)),
                ('minors_profession', models.CharField(default=b'NA', max_length=256, verbose_name=b'What are they doing for work?')),
                ('minors_encouraged', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did you encourage them to take this job?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training', models.CharField(default=b'NA', max_length=2, verbose_name=b'Did they receive any vocational training?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('minors_training_type', models.CharField(default=b'NA', max_length=256, verbose_name=b'What kind of vocational training did they receive?')),
                ('enrolled', models.CharField(default=b'N', max_length=2, verbose_name=b'Currently enrolled?', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('grade_last', models.IntegerField(default=1, choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('reasons', models.TextField(default=b'NA')),
                ('notes', models.TextField(default=b'NA')),
                ('student_id', models.ForeignKey(to='mande.IntakeSurvey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostExitSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_exit_survey_date', models.DateField(default=datetime.date.today, verbose_name=b'Date of Survey')),
                ('exit_date', models.DateField(verbose_name=b'Exit Date')),
                ('early_exit', models.CharField(default=b'NA', max_length=2, verbose_name=b'Early (Pre 6th Grade) Exit', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('last_grade', models.IntegerField(default=1, max_length=1, verbose_name=b'Last Grade at AH', choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('father_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Father's Profession")),
                ('father_employment', models.CharField(default=1, max_length=1, verbose_name=b"Father's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('mother_profession', models.CharField(default=b'NA', max_length=64, verbose_name=b"Mother's Profession")),
                ('mother_employment', models.CharField(default=1, max_length=1, verbose_name=b"Mother's Employment", choices=[(b'1', b'1 - Very Low Wage'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'Middle Class (or higher)')])),
                ('minors', models.IntegerField(default=0, verbose_name=b'How many children (under 18) are working?')),
                ('enrolled', models.CharField(default=b'NA', max_length=2, verbose_name=b'Currently in school? [Primary Child]', choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'NA', b'Not Applicable')])),
                ('grade_current', models.IntegerField(default=1, verbose_name=b'Current Grade', choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('grade_previous', models.IntegerField(default=1, verbose_name=b'Last Grade attended?', choices=[(0, b'Not Enrolled'), (1, b'Grade 1'), (2, b'Grade 2'), (3, b'Grade 3'), (4, b'Grade 4'), (5, b'Grade 5'), (6, b'Grade 6')])),
                ('reasons', models.TextField(verbose_name=b'Reasons for not attending')),
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
                ('school_name', models.CharField(max_length=128, verbose_name=b'School Name')),
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
                ('academic_notes', models.TextField(default=b'NA', verbose_name=b'Academic Growth Notes')),
                ('academic_score', models.IntegerField(default=1, verbose_name=b'Academic Growth Score')),
                ('study_notes', models.TextField(default=b'NA', verbose_name=b'Study/Learning Skills Notes')),
                ('study_score', models.IntegerField(default=1, verbose_name=b'Study/Learning Skills Score')),
                ('personal_notes', models.TextField(default=b'NA', verbose_name=b'Life Skills/Personal Development Notes')),
                ('personal_score', models.IntegerField(default=1, verbose_name=b'Life Skills/Personal Development Score')),
                ('hygiene_notes', models.TextField(default=b'NA', verbose_name=b'Hygeine Knowledge Notes')),
                ('hygiene_score', models.IntegerField(default=1, verbose_name=b'Hygeine Score')),
                ('faith_notes', models.TextField(default=b'NA', verbose_name=b'Christian Growth Notes')),
                ('faith_score', models.IntegerField(default=1, verbose_name=b'Christian Growth Score')),
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
            model_name='intakeinternal',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
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
        migrations.AddField(
            model_name='classroom',
            name='school_id',
            field=models.ForeignKey(to='mande.School'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendancedaysoffered',
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
        migrations.AddField(
            model_name='academic',
            name='classroom_id',
            field=models.ForeignKey(to='mande.Classroom'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='academic',
            name='student_id',
            field=models.ForeignKey(to='mande.IntakeSurvey'),
            preserve_default=True,
        ),
    ]
