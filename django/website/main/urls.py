from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import (
    StandardView,
    StandardRootView,
    StandardLangView,
    LatestView,
    CommitRedirectView,
    SchemaView,
    ExampleView
)

urlpatterns = patterns('',
    # commit redirect views - to catch people using old URLs
    url(r'^r/commit/(?P<release>[a-zA-Z0-9_.-]+)/(?P<old_url_path>[-./\w]+)$', CommitRedirectView.as_view(), name='commit-redirect'),

    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/$', StandardRootView.as_view(), name='standard-root'),
    # TODO: should lang be more than 2 characters?
    # lang code could be "en" or "en-gb" or "en_gb"
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z]{2}([-_][a-z]{2,5})?)/$', StandardLangView.as_view(), name='standard-lang'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z]{2}([-_][a-z]{2,5})?)/(?P<path>[-.\w/]+)/$', StandardView.as_view(), name='standard'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaView.as_view(), name='schema'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/example/(?P<file_name>[a-zA-Z0-9_.-]+)$', ExampleView.as_view(), name='example'),
    url(r'^$', LatestView.as_view(), name='latest'),
)
