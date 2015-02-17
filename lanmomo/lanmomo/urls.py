from django.conf.urls import patterns, include, url
from django.contrib import admin
from main import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lanmomo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', views.home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/(?P<key>\w+)/$', views.models_list),
    url(r'^api/(?P<key>\w+)/(?P<pk>[0-9]+)/$', views.models_detail),
)
