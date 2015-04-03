from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin
from mande import views

urlpatterns = patterns('',
    url(r'^', include('mande.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
)
