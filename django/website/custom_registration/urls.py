from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views
from .views import CustomRegistrationView


urlpatterns = patterns('',
    url(r'^register/$', CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^', include('registration.backends.simple.urls')),
)
