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
    url(r'^attendance/calendar/(?P<classroom_id>\d+)/$', views.attendance_days, name='attendance_days'),

    url(r'^attendance/take/(?P<classroom_id>\d+)/$', views.take_attendance, name='take_attendance'),





)
