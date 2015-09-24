from django.conf.urls import patterns, include, url

from parlhand import api,events,views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'events', events.EventList,base_name="events")
#router.register(r'events/on_this_day', events.OnThisDayList,base_name="on_this_day")
router.register(r'popolo/parliamentarians', api.ParliamentarianViewSet,base_name="parliamentarians")
router.register(r'popolo/parliamentariannames', api.ParliamentarianNameComponentViewSet,base_name="parliamentariannames")
router.register(r'popolo/party', api.PartyViewSet,base_name="party")

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^auth', include('rest_framework.urls', namespace='rest_framework')),
    )


