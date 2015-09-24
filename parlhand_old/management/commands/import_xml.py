from __future__ import print_function
import os
import re

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import reversion
from lxml import etree

from parlhand import models
from parlhand.management.commands import utils as import_utils

class Command(BaseCommand):
    args = 'xml_file_name'
    help = 'Import a single ParlBibXML file and create a new record or merge it with an existing record'

    def handle(self, *args, **options):
        for input_file in args:
            self.process_xml_file(input_file)

    def process_xml_file(self,file):
        print("importing - ",file)
        with open(file, 'r') as imported_xml:
            with transaction.atomic(), reversion.create_revision():
                self.parl_xml = etree.parse(imported_xml).xpath('/biog.entry')[0]
    
                ph_id = self.parl_xml.xpath('name.id')[0].text
                if ph_id is None or ph_id == "":
                    raise Exception
                self.person,created = models.Person.objects.get_or_create(phid=ph_id)
                print(self.person)
                
                #self.run(self.update_ministerials,'ministerial.appointments')
                self.run(self.update_committees,'committee.service')
                self.run(self.update_party_positions,'party.positions')
                self.run(self.update_military,'military.service')
                self.run(self.update_image,'image',os.path.dirname(imported_xml.name))
                
                reversion.set_comment("Updated contents of %s (%s) from file: %s"%(self.person.surname,self.person.phid,file))
        print("Done")

    def run(self,func,xpath,*args):
        elem = self.parl_xml.xpath(xpath)
        if len(elem) > 0:
            return func(self.person,elem[0],*args)
    
    def make_party_membership(self,person,data):
        party,created = models.Party.objects.get_or_create(code=data[1],defaults={'name':data[0]})
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

    def update_image(self,person,image,path):
        if not person.picture and image is not None:
            try:
                print("Added image -",os.path.join(path,image.text))
                image_file = open(os.path.join(path,image.text), "rb")
                django_file = File(image_file)
    
                person.picture.save(
                    image.text,
                    django_file
                    )
            
                person.save()
            except:
                print("ERROR: ---- ","Picture upload failed for -",person)

    def update_ministerials(self,person,ministerials):
        print('Updating ministerial positions')
        for p in ministerials.findall('para'):
            # clean up text
            text = p.text.strip().strip('.')
            text = re.sub("\s\s+" , " ", text)

            try:
                position,dates = text.split(' from ',1)
                dates = dates.split(' to ',1)
                if len(dates) == 2:
                    start,end = dates
                else:
                    start = dates[0]
                    end = None
    
                #print([position,import_utils.str_to_date(start),import_utils.str_to_date(end)])
                
                ministerial_position,c = models.MinisterialPosition.objects.get_or_create(name=position)
                models.MinisterialAppointment.objects.get_or_create(
                    person=person,
                    position=ministerial_position,
                    start_date=import_utils.str_to_date(start),
                    defaults={
                        'end_date':import_utils.str_to_date(end)
                    })
            except:
                print("ERROR: ---- ","Failed on text-",text)
                
    def update_committees(self,person,committees):
        print('Updating committee positions')
        #Need an array as many committees might be on the same line

        for p in committees.findall('para'):
            # clean up text
            text = p.text.strip().strip('.')
            text = re.sub("\s\s+" , " ", text)

            try:
                comm_type, comms = text.split(': ',1)
            except:
                print("ERROR: ----","Committee failed for whole line:",text)
            for comm in comms.split(';'):
                comm = comm.strip()
                try:
                    comm_name = comm.split('from',1)[0].strip()
                    dates = "from"+comm.split('from',1)[1]
                    
                    # If you don't understand regular expressions, view the one below in https://regex101.com/ for a full breakdown
                    # The short version is it finds most possible dates for a committee membership from relatively freetext string
                    date_regex = "(?:from (?P<start>[\d\.]+)(?:(?P<notes>.*?)?(?: to (?P<end>[\d\.]+)))?)"
                    
                    dates = re.findall(date_regex,dates)
    
                    committee,c = models.Committee.objects.get_or_create(name=comm_name,type=comm_type)
                    for date in dates:
                        start = date[0]
                        notes = date[1].strip()
                        end = date[2]
            
                        models.CommitteeMembership.objects.update_or_create(
                            person=person,
                            committee=committee,
                            start_date=import_utils.str_to_date(start),
                            defaults={
                                'notes':notes,
                                'end_date':import_utils.str_to_date(end)
                            })
                except Exception, e:
                    print("ERROR: ----","Committee failed at:",comm)

    def update_party_positions(self,person,party_pos):
        for p in party_pos.findall('para'):
            # clean up text
            text = p.text.strip().strip('.')
            text = re.sub("\s\s+" , " ", text)


            for pos in text.split(';'):
                pos = pos.strip()
                pos_party = None
                for party in models.Party.objects.all():
                    if party.code in pos:
                        pos_party = party
                if pos_party is None:
                    if "LNP" in pos or 'Liberal Party' in pos or 'Young Liberal' in pos:
                        party = models.Party.objects.get(code='LP')
                    if 'Labor' in pos:
                        party = models.Party.objects.get(code='ALP')
                    
                if pos_party:
                    for m in re.findall('\d\d\d\d-\d\d',pos):
                        _from,_to = m.split('-',1)
                        _from = _from+"-00-00"
                        _to = '19'+_to+"-00-00"
                        models.PartyPosition.objects.get_or_create(
                            person=person,party=pos_party,position=pos,
                            start_date=_from,
                            end_date=_to,
                            )

    def update_military(self,person,military):
        for p in military.findall('para'):
            text = p.text.strip().strip('.')
            text = re.sub("\s\s+" , " ", text)
            
            models.MilitaryService.objects.update_or_create(
                person=person,
                notes=text,
                )
