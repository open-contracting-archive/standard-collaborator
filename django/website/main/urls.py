from django.conf.urls import patterns, include, url
from .views import StandardView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', StandardView.as_view(), name='home'),
)
