"""
Add a scripts section.
"""

from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        self.model.add_to_class('scripts', models.TextField(help_text="Extra external scripts to run",null=True,blank=True))
        self.model.add_to_class('script', models.TextField(help_text="Scripts inserted and run",null=True,blank=True))

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options(_('Scripts'), {
            'fields': ('scripts','script'),
            'classes': ('collapse',),
        })
