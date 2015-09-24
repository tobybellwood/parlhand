from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from parlhand.views import ParliamentSearchView

import data_interrogator
from mezzanine.core.views import direct_to_template
from mezzanine.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'parlhand.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^$', 'parlhand.views.home', name='home'),
    url(r'^parliamentarian/(?P<phid>.+)$', 'parlhand.views.parliamentarian', name='parliamentarian'),
    url(r'^current/$', 'parlhand.views.all_current', name='all_current'),
    url(r'^current/(?P<chamber>senate|house)/', 'parlhand.views.current_chamber', name='current'),
    url(r'^current/ministry/', 'parlhand.views.current_ministry', name='current_ministry'),
    #url(r'^current/(?P<chamber>senate|house)/(?P<phid>.+)$', 'parlhand.views.current', name='current'),
    url(r'^tables/all_parliamentarians', 'parlhand.views.all_parliamentarians', name='all_parliamentarians'),
    url(r'^tables/explorer', 'parlhand.views.custom_table', name='data_explorer'),
    url(r'^stuff/ministerialposition/(?P<mid>.+)', 'parlhand.views.ministerialposition', name='ministerialposition'),
    url(r'^stuff/ministry/(?P<mid>.+)', 'parlhand.views.ministry', name='ministry'),
    url(r'^electorate/(?P<eid>.+)', 'parlhand.views.electorate', name='electorate'),
    url(r'^interrogation/', include(data_interrogator.urls)),

    #url(r'^topics/?$', 'parlhand.views.topics', name='topics'),
    url(r'^topics/women_in_parliament$', 'parlhand.views.women_in_parliament', name='women_in_parliament'),
    url(r'^topics/parties', 'parlhand.views.parties_and_parl', name='parties_and_parl'),
    url(r'^events/', 'parlhand.views.events_api', name='events_api'),
    url(r'^topics/longest_serving', 'parlhand.views.longest_serving', name='longest_serving'),

    url(r'^plate/', include('django_spaghetti.urls')),
    
    url(r'^search/?$', ParliamentSearchView.as_view(), name='search_view'),
)



urlpatterns += patterns('',
    url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),
    ("^", include("mezzanine.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from parlhand import api
from rest_framework import routers

# Create a router and register our viewsets with it.
# Must add base_names to prevent clashes when REST-API tries to automatically make URLs.
router = routers.DefaultRouter()
router.register(r'parliamentarians', api.ParliamentarianViewSet,base_name="parliamentarians")
router.register(r'senators', api.SenatorViewSet, base_name="senators")
router.register(r'members', api.MemberViewSet,base_name="members")
router.register(r'electorates', api.ElectorateViewSet,base_name="electorates")

urlpatterns = urlpatterns+patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    )
