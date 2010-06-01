from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.dashboard', name='dashboard'),

    # Feedback actions
    url(r'^sad/?', 'feedback.views.give_feedback', {'positive': False},
        name='feedback.sad'),
    url(r'^happy/?', 'feedback.views.give_feedback', {'positive': True},
        name='feedback.happy'),
    url(r'^thanks/?', direct_to_template, {'template': 'feedback/thanks.html'},
        name='feedback.thanks'),

    (r'^dashboard/', include('dashboard.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)