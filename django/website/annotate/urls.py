from django.conf.urls import patterns, include, url
from .views import GetToken

urlpatterns = patterns('',
    # Examples:
    url(r'^token/$', GetToken.as_view(), name='token'),
)
