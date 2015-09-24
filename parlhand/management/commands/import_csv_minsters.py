from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from parlhand import models
import csv
from parlhand.management.commands import utils as import_utils
import reversion

class Command(BaseCommand):
    args = 'csv_file_name'
    help = ''

    def handle(self, *args, **options):
        file = args[0]
        print("importing - ",file)
        with open(file, 'r') as imported_csv:
            reader = csv.reader(imported_csv)  # creates the reader object
            next(reader, None)  # skip the headers
            for i,row in enumerate(reader):   # iterates the rows of the file in orders
                if i%25 == 1:
                    print('.',end="")
                #for col in row:
                phid = row[0].replace("\"","")
                try:
                    person = models.Person.objects.get(phid=phid)
                    self.update_ministerials(person,row)
                except models.Person.DoesNotExist:
                    print("person %s not in database yet!!"%phid)
        print("Done")

    def update_ministerials(self,person,row):
        #print('Updating ministerial positions')
        # clean up text
        ministry,c = models.Ministry.objects.get_or_create(name=row[-1])

        start = row[7]
        end = row[8]
        position = row[3]
        _type = row[6]
        if row[5] == "Yes":
            _type = "Cabinet"

        ministerial_position,c = models.MinisterialPosition.objects.get_or_create(name=position)
        models.MinisterialAppointment.objects.get_or_create(
            person=person,
            position=ministerial_position,
            ministry=ministry,
            type = models.MinisterialAppointment.TYPES[_type],
            end_date = import_utils.str_to_date(end),
            start_date=import_utils.str_to_date(start),
            )

    def make_party_membership(self,person,data):
        party_code = data[1].upper().strip()
        party,created = models.Party.objects.get_or_create(code=party_code,defaults={'name':data[0]})
        mem,c = models.PartyMembership.objects.get_or_create(
                person = person,
                party = party,
                start_date = import_utils.str_to_date(data[3]),
                end_date = import_utils.str_to_date(data[4]),
                )