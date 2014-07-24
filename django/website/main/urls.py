from django.conf.urls import patterns, include, url
from .views import (
    StandardView,
    LatestView,
    CommitView,
    SchemaView,
    SchemaView,
    SchemaCommitView
)

urlpatterns = patterns('',
    # Examples:
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/$', StandardView.as_view(), name='standard'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaView.as_view(), name='schema'),
    url(r'^r/commit/(?P<commitid>[a-zA-Z0-9_.-]+)/$', CommitView.as_view(), name='commit'),
    url(r'^r/commit/(?P<commitid>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaCommitView.as_view(), name='schema-commit'),
    url(r'^$', LatestView.as_view(), name='latest'),
)
