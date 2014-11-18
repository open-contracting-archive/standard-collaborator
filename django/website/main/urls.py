from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import (
    StandardView,
    StandardRootView,
    StandardLangView,
    LegacyRedirectView,
    LegacyRootView,
    LatestView,
    CommitRedirectView,
    SchemaView,
    ExampleView,
    AssetView
)

urlpatterns = patterns(
    '',
    # commit redirect views - to catch people using old URLs
    url(r'^r/commit/(?P<release>[a-zA-Z0-9_.-]+)/(?P<old_url_path>[-./\w]+)$', CommitRedirectView.as_view(), name='commit-redirect'),
    # see below for what this should match
    url(r'^r/0__3__3/$', LatestView.as_view()),
    url(r'^r/(?P<release>(0__3__[0-3]|0__[12]__0|draft-june-(1-|5-|20_)2014(_2)?))/$', LegacyRedirectView.as_view(), name='legacy-redirect'),
    url(r'^legacy/r/(?P<release>(0__3__[0-3]|0__[12]__0|draft-june-(1-|5-|20_)2014(_2)?))/$', LegacyRootView.as_view(), name='legacy-root'),

    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/$', StandardRootView.as_view(), name='standard-root'),
    # TODO: should lang be more than 2 characters?
    # lang code could be "en" or "en-gb" or "en_gb"
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z]{2}([-_][a-z]{2,5})?)/$', StandardLangView.as_view(), name='standard-lang'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<lang>[a-z]{2}([-_][a-z]{2,5})?)/(?P<path>[-.\w/]+)/$', StandardView.as_view(), name='standard'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/(?P<schema_name>[a-zA-Z0-9_.-]+).json$', SchemaView.as_view(), name='schema'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/example/(?P<file_name>[a-zA-Z0-9_.-]+)$', ExampleView.as_view(), name='example'),
    url(r'^r/(?P<release>[a-zA-Z0-9_.-]+)/assets/(?P<file_name>[a-zA-Z0-9_.-]+)$', AssetView.as_view(), name='example'),
    url(r'^$', LatestView.as_view(), name='latest'),
)

# the legacy view should match the following tags:
# 0__1__0
# 0__2__0
# 0__3__0
# 0__3__1
# 0__3__2
# 0__3__3
# draft-june-1-2014
# draft-june-5-2014
# draft_june_20_2014
# draft_june_20_2014_2
#
# leading to the regex
#
# (0__3__[0-3]|0__[12]__0|draft-june-(1-|5-|20_)2014(_2)?)
