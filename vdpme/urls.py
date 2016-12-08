from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin
from mande import views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
)
new_patterns = i18n_patterns('',url(r'^', include('mande.urls')))
urlpatterns += new_patterns
