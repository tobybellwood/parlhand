from django.conf.urls import patterns, include, url
from parlhand.views import ParliamentSearchView

urlpatterns = patterns('parlhand.views',
    url(r'^parliamentarian/(?P<phid>.+)', 'parliamentarian', name='parliamentarian'),
    url(r'^parliament/(?P<number>.+)', 'parliament', name='parliament'),
    url(r'^current/(?P<chamber>senate|house)/', 'current_chamber', name='current'),
    url(r'^tables/all_parliamentarians', 'all_parliamentarians', name='all_parliamentarians'),
    url(r'^data/explorer', 'custom_table', name='data_explorer'),
    url(r'^stuff/ministerialposition/(?P<mid>.+)', 'ministerialposition', name='ministerialposition'),
    url(r'^stuff/ministry/(?P<ministry_number>.+)', 'ministry', name='ministry'),
    url(r'^party/(?P<code>.*)', 'party', name='party'),
    url(r'^committee/(?P<cid>.*)', 'committee', name='committee'),
    url(r'^electorate/(?P<eid>.+)', 'electorate', name='electorate'),
    
    url(r'^on_this_day/(?P<month>[0-9][0-9]?)/(?P<day>[0-9][0-9]?)/?', 'on_this_day', name='on_this_day'),
    url(r'^on_this_day/?', 'on_this_day', name='on_this_day'),
    
    url(r'^dyncss/(?P<name>.+)\.css', 'dynamic_css', name='dynamic_css'),

    url(r'^search/?$', ParliamentSearchView.as_view(), name='search_view'),
)