from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myapp.views.home', name='home'),
    url(r'^', include('main.urls')),
    url(r'^annotate/', include('annotate.urls')),
    url(r'^accounts/', include('custom_registration.urls')),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # This requires that static files are served from the 'static' folder.
    # The apache conf is set up to do this for you, but you will need to do it
    # on dev
    (r'/favicon.ico', 'django.views.generic.base.RedirectView',
        {'url':  '{0}images/favicon.ico'.format(settings.STATIC_URL)}),
)
