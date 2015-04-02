from django.conf.urls import patterns, url

from mande import views
urlpatterns = patterns('',
    # ex: /mande/
    url(r'^$', views.index, name='index'),
    # ex: /mande/students/
    url(r'^students/$', views.student_list, name='student_list'),
    # ex: /mande/students/4
    url(r'^students/(?P<student_id>\d+)/$', views.student_detail, name='student_detail'),
    # ex: /mande/reports/
    url(r'^reports/$', views.report_list, name='report_list'),

    # ex: /mande/sites/
    url(r'^sites/$', views.site_list, name='site_list'),

    url(r'^attendance/$', views.attendance, name='attendance'),
    url(r'^attendance/calendar$', views.attendance_calendar, name='attendance_calendar'),
    url(r'^attendance/calendar/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.attendance_days, name='attendance_days'),

    url(r'^attendance/take/$', views.take_attendance, name='take_attendance'),
    url(r'^attendance/take/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.take_class_attendance, name='take_class_attendance'),

    url(r'^surveys/intake/$', views.intake_survey, name='intake_survey'),
    url(r'^surveys/intake_update/(?P<student_id>\d+)/$', views.intake_update, name='intake_update'),
    url(r'^surveys/intake_update/$', views.intake_update, name='intake_update'),

    url(r'^surveys/exit/(?P<student_id>\d+)/$', views.exit_survey, name='exit_survey'),
    url(r'^surveys/exit/$', views.exit_survey, name='exit_survey'),

    url(r'^surveys/post_exit/(?P<student_id>\d+)/$', views.post_exit_survey, name='post_exit_survey'),
    url(r'^surveys/post_exit/$', views.post_exit_survey_list, name='post_exit_survey'),

    url(r'^surveys/spiritualactivities/(?P<student_id>\d+)/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),
    url(r'^surveys/spiritualactivities/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),

    url(r'^school-management/discipline/(?P<student_id>\d+)/$', views.discipline_form, name='discipline_form'),
    url(r'^school-management/discipline/$', views.discipline_form, name='discipline_form'),

    url(r'^school-management/teachers/$', views.teacher_form, name='teacher_form'),
    url(r'^school-management/teachers/(?P<teacher_id>\d+)/$', views.teacher_form, name='teacher_form'),

    url(r'^school-management/classrooms/$', views.classroom_form, name='classroom_form'),
    url(r'^school-management/classrooms/(?P<classroom_id>\d+)/$', views.classroom_form, name='classroom_form'),

    url(r'^school-management/classrooms/assignment/$', views.classroomteacher_form, name='classroomteacher_form'),
    url(r'^school-management/classrooms/assignment/(?P<teacher_id>\d+)/$', views.classroomteacher_form, name='classroomteacher_form'),

    url(r'^school-management/enrollment/(?P<student_id>\d+)/$', views.classroomenrollment_form, name='classroomenrollment_form'),
    url(r'^school-management/enrollment/$', views.classroomenrollment_form, name='classroomenrollment_form'),


    url(r'^school-management/academics/$', views.academic_select, name='academic_select'),
    url(r'^school-management/academics/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/$', views.academic_form, name='academic_form'),
    url(r'^school-management/academics/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/(?P<grade_id>\d+)/$', views.academic_form, name='academic_form'),

    url(r'^success/$', views.survey_success, name='survey_success'),




)
