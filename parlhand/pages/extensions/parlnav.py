"""
Add a "featured" field to objects so admins can better direct top content.
"""

from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        self.model.add_to_class('separator', models.BooleanField(_('separator'), default=False))
        self.model.add_to_class('navtitle', models.CharField(_('Navigation Title'),max_length=255,null=True,blank=True))

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options(_('Separator'), {
            'fields': ('separator','navtitle'),
            'classes': ('collapse',),
        })