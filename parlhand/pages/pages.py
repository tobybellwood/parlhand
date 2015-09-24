from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from data_interrogator import interrogate

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.medialibrary.models import MediaFileContent

Page.register_extensions(
    'feincms.module.extensions.datepublisher',
    'feincms.module.extensions.featured',
    'feincms.module.page.extensions.navigation',
    'feincms.module.page.extensions.navigationgroups',
    'parlhand.pages.extensions.parlnav',
    'parlhand.pages.extensions.scripts',
)

Page.register_templates({
    'title': _('Standard template'),
    'path': 'cms_page/page.html',
    'regions': (
        ('main', _('Main content area')),
        #('sidebar', _('Sidebar'), 'inherited'),
    ),
})

Page.create_content_type(RichTextContent)
Page.create_content_type(MediaFileContent, TYPE_CHOICES=(
    ('default', _('default')),
    ('lightbox', _('lightbox')),
))

class DataTableContent(models.Model):
    table = models.ForeignKey('data_interrogator.DataTable')

    class Meta:
        abstract = True

    def render(self, **kwargs):
        data = {}
        data['table'] = self.table

        return render_to_string('data_interrogator/embedded.html', data)

Page.create_content_type(DataTableContent)
