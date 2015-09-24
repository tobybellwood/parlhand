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
                person,created = models.Person.objects.get_or_create(phid=phid)
                person.sen_id = row[1].strip() or None
                person.rep_id = row[2].strip() or None
                person.first_names = row[3].split(',',1)[1].strip()
                person.surname = row[3].split(',',1)[0].strip()
                person.honorifics = row[5]
                person.preferred_name = row[6]
                person.postnomials = row[8]
                person.biography = row[18]
                person.gender = row[11]
                person.date_of_birth = import_utils.str_to_date(row[12])
                person.place_of_birth = row[13]
                person.date_of_death = import_utils.str_to_date(row[14])
                person.save()
                
                # Make senators and members seats
                for s in [20,29,38,47]:
                    if row[s] != "":
                        self.make_division(person,row[s:s+9])
                
                # Make parties
                for s in [57,62,67]:
                    if row[s] != "":
                        self.make_party_membership(person,row[s:s+5])
        print("Done")
    def make_party_membership(self,person,data):
        party_code = data[1].upper().strip()
        party,created = models.Party.objects.get_or_create(code=party_code,defaults={'name':data[0]})
        mem,c = models.PartyMembership.objects.get_or_create(
                person = person,
                party = party,
                start_date = import_utils.str_to_date(data[3]),
                end_date = import_utils.str_to_date(data[4]),
                )

    def make_division(self,person,data):
        if data[0] == 'Member':
            self.make_member(person,data)
        elif data[0] == 'Senator':
            self.make_senator(person,data)

    def make_senator(self,person,data):
        state,created = models.State.objects.get_or_create(code=data[3], defaults={'name':data[2]})
        electorate,created = models.Electorate.objects.get_or_create(
            name=data[2],
            state=state,
            )
        sen,c = models.Service.objects.get_or_create(
                person = person,
                electorate = electorate,
                seat_type = models.Service.SEAT_TYPES.Senator,
                start_date = import_utils.str_to_date(data[5]),
                end_date = import_utils.str_to_date(data[6]),
                defaults = {
                    'start_reason': data[4],
                    'end_reason': data[8],
                }
            )
        
    def make_member(self,person,data):
        state,created = models.State.objects.get_or_create(code=data[3])
        electorate,created = models.Electorate.objects.get_or_create(
            name=data[2],
            state=state,
            )
        rep,c = models.Service.objects.get_or_create(
                person = person,
                electorate = electorate,
                seat_type = models.Service.SEAT_TYPES.Member,
                start_date = import_utils.str_to_date(data[5]),
                end_date = import_utils.str_to_date(data[6]),
                defaults = {
                    'start_reason': data[4],
                    'end_reason': data[8],
                }
            )
            