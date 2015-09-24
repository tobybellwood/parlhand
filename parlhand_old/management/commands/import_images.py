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
            phid, ext = img.rsplit('.',1)
            if ext.lower() not in extensions:
                continue

            try:
                person = models.Person.objects.get(phid__iexact=phid)
                image_file = open(os.path.join(imgdir,img), "rb")
                django_file = File(image_file)
    
                person.picture.save(img,django_file)
                person.save()
            except models.Person.DoesNotExist:
                print("ERROR: ---- No record for -",img)
            except:
                print("ERROR: ---- ","Picture upload failed for -",person.full_name)

        print("Done")
