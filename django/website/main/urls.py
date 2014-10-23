from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import (
    StandardView,
    StandardRootView,
    StandardLangView,
    LatestView,
    CommitView,
    SchemaView,
    SchemaCommitView
)

urlpatterns = patterns('',
    # Examples:
    # TODO: do we want to keep the commit views?  Ask Tim?
    # TODO: if we do we need commit redirect views
    url(r'^r/commit/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z][a-z])/(?P<path>[-.\w/]+)/$', CommitView.as_view(), name='commit'),
    url(r'^r/commit/(?P<release>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaCommitView.as_view(), name='schema-commit'),

    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/$', StandardRootView.as_view(), name='standard-root'),
    # TODO: should lang be more than 2 characters?
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z][a-z])/$', StandardLangView.as_view(), name='standard-lang'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z][a-z])/(?P<path>[-.\w/]+)/$', StandardView.as_view(), name='standard'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaView.as_view(), name='schema'),
    url(r'^$', LatestView.as_view(), name='latest'),
)
