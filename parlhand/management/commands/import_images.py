from __future__ import print_function
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from parlhand import models

import glob, os

class Command(BaseCommand):
    args = 'csv_file_name'
    help = ''

    def handle(self, *args, **options):
        imgdir = args[0]
        extensions = ['jpg','png','jpeg']
        print("importing images from - ",imgdir)

        for img in os.listdir(imgdir):
            filename, ext = img.rsplit('.',1)
            if ext.lower() not in extensions:
                continue

            try:
                code = filename.split('_')[0]
                if code.startswith('H'):
                    person = models.Person.objects.get(rep_id__iexact=code)
                elif code.startswith('S'):
                    person = models.Person.objects.get(sen_id__iexact=code)
                else:
                    person = models.Person.objects.get(phid__iexact=code)
                image_file = open(os.path.join(imgdir,img), "rb")
                django_file = File(image_file)
    
                person.image.save(img,django_file)
                person.save()
            except models.Person.DoesNotExist:
                print("ERROR: ---- No record for -",img)
            except:
                print("ERROR: ---- ","Picture upload failed for -",person.name)

        print("Done")
