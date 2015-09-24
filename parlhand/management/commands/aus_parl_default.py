from __future__ import print_function
import os
import yaml
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
import data_interrogator
from feincms.module.page.models import Page
from django.contrib.contenttypes.models import ContentType
from optparse import make_option

RichTextContent = ContentType.objects.get(app_label='page',model='richtextcontent').model_class()
DataTable =  ContentType.objects.get(app_label='page',model='datatablecontent').model_class()

x=[(u'page', u'datatablecontent'),
 (u'page', u'mediafilecontent'),
 (u'page', u'page'),
 (u'page', u'richtextcontent')]


def file_as_rich_text(parent,filename,ordering=0):
    with open(filename, 'r') as content_file:
        return parent.richtextcontent_set.add(RichTextContent(parent=parent,region='main',text=content_file.read()))

def add_richtext(parent,text,ordering=0):
    return parent.richtextcontent_set.add(RichTextContent(parent=parent,region='main',text=text,ordering=0))

class Command(BaseCommand):
    args = ''
    help = 'Setup aus parl details'
    option_list = BaseCommand.option_list + (
        make_option('-D','--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Turn on debug'),
    )
    
    def handle(self, *args, **options):
        directory = args[0]
        self.debug_mode = options['debug']
        self.retry = []
        worked = 0
        before = Page.objects.all().count()
        for root, dirs, files in os.walk(directory):
            path = root.split('/')
            print((len(path) - 1) *'---' , os.path.basename(root))
            for file in sorted(files):
                print(len(path)*'---', file)
                if file.endswith('yaml'):
                    success = self.load_file(os.path.join(root,file))
                    if success:
                        worked += 1
        print(self.retry)
        print('Loaded',worked)
        print('In DB',Page.objects.all().count()-before)
        return
    
    def load_file(self,filename):
        success = True
        with open(filename, 'r') as page:
            try:
                f=yaml.load(page)
                defaults = {
                        'title':f['title'],
                        'in_navigation':f.get('in_navigation',True),
                        'navigation_group':f.get('navigation_group','Default'),
                        'featured':f.get('featured',False),
                        'separator':f.get('separator',False),
                        'navtitle':f.get('navtitle',None),
                        'script': f.get('script',''),
                        'scripts': f.get('scripts',''),
                        }
                
                if f.get('parent_slug',None):
                    defaults['parent'] = Page.objects.get(slug=f.get('parent_slug'))
                if f.get('override_url',None):
                    defaults['override_url'] = f.get('override_url')
                if f.get('redirect_to',None):
                    defaults['redirect_to'] = f.get('redirect_to')
                p,created = Page.objects.get_or_create(slug=f['slug'],
                    defaults = defaults)
                if f.get('text',None):
                    add_richtext(p,f.get('text'))
                if f.get('table',None):
                    table = data_interrogator.models.DataTable.objects.filter(title__icontains=f['table']).first()
                    p.datatablecontent_set.add(DataTable(parent=p,region='main',table=table,ordering=1))
                if f.get('tables',None):
                    for i,t in enumerate(f.get('tables')):
                        table = data_interrogator.models.DataTable.objects.filter(title__icontains=t).first()
                        p.datatablecontent_set.add(DataTable(parent=p,region='main',table=table,ordering=i+1))
            except:
                success = False
                
                if self.debug_mode:
                    raise
        if not success:
            self.retry.append(filename)
        return success