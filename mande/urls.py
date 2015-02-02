from django.conf.urls import patterns, url

from mande import views
urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<student_id>\d+)/$', views.student_detail, name='student_detail'),
    # ex: /polls/5/results/
    url(r'^(?P<student_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    url(r'^(?P<student_id>\d+)/vote/$', views.vote, name='vote'),

)
