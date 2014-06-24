from django.conf.urls import patterns, include, url
from .views import StandardView, LatestView

urlpatterns = patterns('',
    # Examples:
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/$', StandardView.as_view(), name='standard'),
    url(r'^r/master/(?P<commit>[a-zA-Z0-9_.-]+)/$', StandardView.as_view(), name='commitid'),
    url(r'^$', LatestView.as_view(), name='latest'),
)
