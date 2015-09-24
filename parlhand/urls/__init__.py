from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
#from parlhand.views import ParliamentSearchView

import data_interrogator

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^', include("parlhand.urls.main",namespace='parlhand')),
    url(r'^s/', include("parlhand.urls.shorteners")),# namespace='parlhand')),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url(r'^grappelli/', include("grappelli.urls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^interrogation/', include(data_interrogator.urls)),
    url(r'^plate/', include('django_spaghetti.urls')),
    url(r'^api/', include("parlhand.urls.api")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += patterns('',
    url(r'', include('feincms.urls')),
)
