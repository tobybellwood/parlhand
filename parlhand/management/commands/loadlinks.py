from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.utils import IntegrityError
from django.db.models.fields.related import ForeignKey
from parlhand import models
import csv
import time
from parlhand.management.commands import utils as import_utils
import reversion
from optparse import make_option

class Command(BaseCommand):
    args = 'csv_file_name'
    help = 'Uploads a set of links. Must be of form: id,note,url'

    option_list = BaseCommand.option_list + (
        make_option('-D','--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Turn on debug'),
        make_option('-s','--separator',
            action='store',
            dest='sep',
            default=',',
            help='Define column separator (default: ,)'),
        make_option('-m','--model',
            action='store',
            dest='model_name',
            default=None,
            help='Define model to insert into (default: uses filename)'),
    )
    def handle(self, *args, **options):
        self.debug_mode = options['debug']
        requested_model = options['model_name']
        separator = options['sep']
        verbosity = int(options['verbosity'])

        if not args or len(args) == 0:
            print(self.help)
            return
        elif len(args) == 1:
            filename = args[0]
        else:
            print("Wrong number of arguments")
            return

        if requested_model is None:
            path,fn = filename.rsplit('/',1)
            app_label,model = fn.rsplit('.')[0:2]
        else:
            app_label,model = requested_model.lower().split('.',1)

        if separator in ['\\t','tab']:
            separator = '\t'

        print(requested_model)

        try:
            model_type = ContentType.objects.get(app_label=app_label,model=model)
            model = model_type.model_class()
        except ContentType.DoesNotExist:
            print("Model does not exist - %s"%requested_model)
            return 
        print("importing file <%s> as links for model <%s>"%(filename,requested_model))
        start_time = time.time()
        with open(filename, 'r') as imported_csv:
            reader = csv.reader(imported_csv,delimiter=separator)  # creates the reader object
            headers = reader.next() # get the headers
            failed = []
            success = []
            skipped = []
            for i,row in enumerate(reader):   # iterates the rows of the file in orders
                if len(failed) > 100:
                    print('something has gone terribly wrong.') 
                    break
                try:
                    with transaction.atomic():
                        pk = clean(row[0])
                        note = clean(row[1])
                        url = clean(row[2])
                        obj = model.objects.get(pk=pk)
                        
                        if not models.popolo.Link.objects.filter(
                                content_type__pk=model_type.id,object_id=pk,
                                note=note,url=url
                        ).exists():
                            l = models.popolo.Link(content_object=obj,note=note,url=url)
                            l.save()
                            success.append(i)
                        else:
                            if verbosity>=2:
                                print("Line %s - skipped"%i)
                                print(verbosity)
                            if verbosity==3:
                                print(row)
                            skipped.append(i)
                    # end transaction
                except Exception as e:
                    if verbosity >=2:
                        print("Line %s - %s"%(i,e))
                    if self.debug_mode:
                        raise
                    failed.append(i)
        elapsed_time = time.time() - start_time
        print("Summary:")
        if verbosity >=1:
            print("  Time taken: %.3f seconds"%elapsed_time)
        print("  Success: %s"%len(success))
        if skipped:
            print("  Skipped: %s"%len(skipped))
        if failed:
            print("  Failed: %s"%len(failed))
            print("  Failed on lines: %s"%str(failed))
        

def clean(string):
    return string.strip('"').strip().replace("\"","")
