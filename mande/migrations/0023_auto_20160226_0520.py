# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mande', '0022_auto_20160204_0437'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academic',
            options={'permissions': (('view_academic', 'Can view academic'),)},
        ),
        migrations.AlterModelOptions(
            name='attendance',
            options={'permissions': (('view_attendance', 'Can view attendance'),)},
        ),
        migrations.AlterModelOptions(
            name='attendancedayoffering',
            options={'permissions': (('view_attendancedayoffering', 'Can view attendance day offering'),)},
        ),
        migrations.AlterModelOptions(
            name='attendancelog',
            options={'permissions': (('view_attendancelog', 'Can view attendance log'),)},
        ),
        migrations.AlterModelOptions(
            name='classroom',
            options={'permissions': (('view_classroom', 'Can view classroom'),)},
        ),
        migrations.AlterModelOptions(
            name='classroomenrollment',
            options={'permissions': (('view_classroomenrollment', 'Can view classroom enrollment'),)},
        ),
        migrations.AlterModelOptions(
            name='classroomteacher',
            options={'permissions': (('view_classroomteacher', 'Can view classroom teacher'),)},
        ),
        migrations.AlterModelOptions(
            name='discipline',
            options={'permissions': (('view_discipline', 'Can view discipline'),)},
        ),
        migrations.AlterModelOptions(
            name='exitsurvey',
            options={'permissions': (('view_exitsurvey', 'Can view exit survey'),)},
        ),
        migrations.AlterModelOptions(
            name='health',
            options={'permissions': (('view_health', 'Can view health'),)},
        ),
        migrations.AlterModelOptions(
            name='intakeinternal',
            options={'permissions': (('view_intakeinternal', 'Can view intake internal'),)},
        ),
        migrations.AlterModelOptions(
            name='intakesurvey',
            options={'permissions': (('view_intakesurvey', 'Can view intake survey'),)},
        ),
        migrations.AlterModelOptions(
            name='intakeupdate',
            options={'permissions': (('view_intakeupdate', 'Can view intake update'),)},
        ),
        migrations.AlterModelOptions(
            name='notificationlog',
            options={'get_latest_by': 'date', 'permissions': (('view_notificationlog', 'Can view notification log'),)},
        ),
        migrations.AlterModelOptions(
            name='postexitsurvey',
            options={'permissions': (('view_postexitsurvey', 'Can view post exit survey'),)},
        ),
        migrations.AlterModelOptions(
            name='school',
            options={'permissions': (('view_school', 'Can view school'),)},
        ),
        migrations.AlterModelOptions(
            name='spiritualactivitiessurvey',
            options={'permissions': (('view_spiritualactivitiessurvey', 'Can view spiritual activities survey'),)},
        ),
        migrations.AlterModelOptions(
            name='studentevaluation',
            options={'permissions': (('view_studentevaluation', 'Can view student evaluation'),)},
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'permissions': (('view_teacher', 'Can view teacher'),)},
        ),
    ]
