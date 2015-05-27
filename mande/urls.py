from django.conf.urls import patterns, url

from mande import views
urlpatterns = patterns('',
    # ex: /mande/
    url(r'^$', views.dashboard, name='index'),
    # ex: /mande/students/
    url(r'^students/$', views.student_list, name='student_list'),
    # ex: /mande/students/4
    url(r'^students/(?P<student_id>\d+)/$', views.student_detail, name='student_detail'),

    url(r'^attendance/$', views.attendance, name='attendance'),
    url(r'^attendance/calendar$', views.attendance_calendar, name='attendance_calendar'),
    url(r'^attendance/calendar/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.attendance_days, name='attendance_days'),

    url(r'^attendance/take/$', views.daily_attendance_report, name='take_attendance'),
    url(r'^attendance/take/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.take_class_attendance, name='take_class_attendance'),

    url(r'^attendance/report/$', views.daily_attendance_report, name='daily_attendance_report'),
    url(r'^attendance/report/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.daily_attendance_report, name='daily_attendance_report'),

    url(r'^attendance/report/absences/$', views.daily_absence_report, name='daily_absence_report'),
    url(r'^attendance/report/absences/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.daily_absence_report, name='daily_absence_report'),

    url(r'^surveys/intake/$', views.intake_survey, name='intake_survey'),
    url(r'^surveys/intake/update/(?P<student_id>\d+)/$', views.intake_update, name='intake_update'),
    url(r'^surveys/intake/update/$', views.intake_update, name='intake_update'),
    url(r'^surveys/intake/internal/$', views.intake_internal, name='intake_internal'),
    url(r'^surveys/intake/internal/(?P<student_id>\d+)/$', views.intake_internal, name='intake_internal'),


    url(r'^surveys/exit/(?P<student_id>\d+)/$', views.exit_survey, name='exit_survey'),
    url(r'^surveys/exit/$', views.exit_survey, name='exit_survey'),

    url(r'^surveys/post_exit/(?P<student_id>\d+)/$', views.post_exit_survey, name='post_exit_survey'),
    url(r'^surveys/post_exit/$', views.post_exit_survey_list, name='post_exit_survey'),

    url(r'^surveys/spiritualactivities/(?P<student_id>\d+)/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),
    url(r'^surveys/spiritualactivities/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),

    url(r'^surveys/health/(?P<student_id>\d+)/$', views.health_form, name='health_form'),
    url(r'^surveys/health/$', views.health_form, name='health_form'),

    url(r'^school-management/discipline/(?P<student_id>\d+)/$', views.discipline_form, name='discipline_form'),
    url(r'^school-management/discipline/$', views.discipline_form, name='discipline_form'),

    url(r'^school-management/teachers/$', views.teacher_form, name='teacher_form'),
    url(r'^school-management/teachers/(?P<teacher_id>\d+)/$', views.teacher_form, name='teacher_form'),

    url(r'^school-management/classrooms/$', views.classroom_form, name='classroom_form'),
    url(r'^school-management/classrooms/(?P<classroom_id>\d+)/$', views.classroom_form, name='classroom_form'),

    url(r'^school-management/classrooms/assignment/$', views.classroomteacher_form, name='classroomteacher_form'),
    url(r'^school-management/classrooms/assignment/(?P<teacher_id>\d+)/$', views.classroomteacher_form, name='classroomteacher_form'),

    url(r'^school-management/enrollment/(?P<classroom_id>\d+)/$', views.classroomenrollment_form, name='classroomenrollment_form'),
    url(r'^school-management/enrollment/(?P<classroom_id>\d+)/(?P<student_id>\d+)/$', views.classroomenrollment_individual, name='classroomenrollment_individual'),
    url(r'^school-management/enrollment/$', views.classroomenrollment_form, name='classroomenrollment_form'),


    url(r'^school-management/academics/$', views.academic_select, name='academic_select'),
    url(r'^school-management/academics/(?P<student_id>\d+)/$', views.academic_form_single, name='academic_form_single'),
    url(r'^school-management/academics/bulk/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/$', views.academic_form, name='academic_form'),
    url(r'^school-management/academics/bulk/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/(?P<grade_id>\d+)/$', views.academic_form, name='academic_form'),

    url(r'^success/$', views.survey_success, name='success'),
    url(r'^log/$', views.notification_log, name='notification_log')




)
