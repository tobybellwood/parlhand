from django.conf.urls import patterns, include, url

urlpatterns = patterns('parlhand.views.shorteners',
    url(r'^(?P<mapper>[a-z])/(?P<ident>.+)$', 'unshorten', name='shortener'),
)