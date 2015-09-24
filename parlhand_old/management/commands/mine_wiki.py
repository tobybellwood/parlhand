from __future__ import print_function
import os
import re
import tempfile
import requests

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

import httplib2
from lxml import etree
from bs4 import BeautifulSoup

from parlhand import models
from parlhand.management.commands import utils as import_utils

class Command(BaseCommand):
    args = 'xml_file_name'
    help = 'Import a single ParlBibXML file and create a new record or merge it with an existing record'

    def handle(self, *args, **options):
        if 'pm' in args or 'all' in args:
            self.mine_prime_ministers()
        if 'dpm' in args or 'all' in args:
            self.mine_deputy_prime_ministers()
        if 'opp' in args or 'all' in args:
            self.mine_opposition_leaders()

    def process_xml_file(self,file):
        print("importing - ",file)
        with open(file, 'r') as imported_xml:
            self.parl_xml = etree.parse(imported_xml).xpath('/biog.entry')[0]

            ph_id = self.parl_xml.xpath('name.id')[0].text
            if ph_id is None or ph_id == "":
                raise Exception
            self.person,created = models.Person.objects.get_or_create(phid=ph_id)
            print(self.person)

        print("Done")

    def mine_prime_ministers(self):
        print("Mining Prime Ministers")
        http = httplib2.Http()
        status, response = http.request('https://en.wikipedia.org/wiki/List_of_Prime_Ministers_of_Australia')
        soup = BeautifulSoup(response,"lxml")
        tables = soup.findAll('table',class_="wikitable")

        rows = [row for row in tables[0].findAll('tr',{'style':"background:#EEEEEE"})]

        for row in rows:
            cols = row.findAll('td')
            
            # Damn you Billy Hughes
            if row.findAll('th') and (row.findAll('th')[0].text or "Billy" in cols[0].text):
                #This row is a new starter row, find the PM and do stuff
                pm = cols[0].text.replace('Sir ','').split('(')[0]
                first_name,last_name = pm.split(' ')
                print(first_name,last_name)
                first_name = first_name.strip()
                last_name = last_name.strip()
                qs = models.Person.objects.filter(surname=last_name,first_names__icontains=first_name)
                if qs.count() == 0:
                    qs = models.Person.objects.filter(surname=last_name,preferred_name__icontains=first_name)
                if qs.count() != 1:
                    if qs.count() < 1:
                        print("ERROR - no PM for -",pm)
                    if qs.count() > 1:
                        print("ERROR - too many PM's for -",pm)
                        print("   found these: ",qs.all())
                    continue
                pm = qs.first()
                
                if not pm.picture:
                    picture = cols[1].findAll('img')[0].get('src')
                    self.scrape_image_for_person(picture,pm)
                start = import_utils.str_to_date(cols[3].text)
                end = import_utils.str_to_date(cols[4].text)
                #self.make_pm(pm,start,end)
            else:
                # Continuation row use prior pm
                if not pm:
                    print(" -- No PM?")
                    continue
                # This is a different prime ministership
                if len(cols) > 2:
                    print(cols)
                    start = import_utils.str_to_date(cols[1].text)
                    end = import_utils.str_to_date(cols[2].text)
                    self.make_pm(pm,start,end)
    
    def mine_deputy_prime_ministers(self):
        print("Mining Deputy Prime Ministers")
        http = httplib2.Http()
        status, response = http.request('https://en.wikipedia.org/wiki/Deputy_Prime_Minister_of_Australia')
        soup = BeautifulSoup(response,"lxml")
        tables = soup.findAll('table',class_="wikitable")

        rows = [row for row in tables[0].findAll('tr')]

        for row in rows[1:]:
            cols = row.findAll('td')
            
            #This row is a new starter row, find the Deputy PM and do stuff
            dpm  = cols[1].text.replace('Sir ','').split('(')[0]

            first,last = dpm.split(' ')
            qs = qs.filter(surname__icontains=last,first_names__icontains=first)
            if qs.count() == 0:
                qs = models.Person.objects.filter(surname__icontains=last,preferred_name__icontains=first)
            if qs.count() != 1:
                if qs.count() < 1:
                    print("ERROR - no Deputy PM for -",dpm)
                if qs.count() > 1:
                    print("ERROR - too many Deputy PM's for -",dpm)
                    print("   found these: ",qs.all())
                continue
            dpm = qs.first()
            
            if not dpm.picture:
                picture = cols[2].findAll('img')
                if picture:
                    self.scrape_image_for_person(picture[0].get('src'),dpm)

            start,end = None,None
            start_loc = row.findAll('span',class_='dtstart')
            end_loc = row.findAll('span',class_='dtend')
            if start_loc:
                start = import_utils.str_to_date(start_loc[0].text)
            if end_loc:
                end = import_utils.str_to_date(end_loc[0].text)
            print("-----",dpm,start_loc,end_loc,start,end)
            #self.make_deputy_pm(dpm,start,end)

    def scrape_image_for_person(self,url,person):
        print("Downloading ",url)
        if url.startswith("//"):
            url = "http:"+url
        request = requests.get(url, stream=True)
        ext = url.rsplit('.',1)[-1]
        filename = "%s.%s"%(person.phid,ext)

        # Was the request OK?
        if request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            return

        lf = tempfile.NamedTemporaryFile()
    
        # Read the streamed image in sections
        for block in request.iter_content(1024 * 8):
            # If no more file then stop
            if not block:
                break
    
            # Write image block to temporary file
            lf.write(block)
    
        # Save the temporary image to the model#
        # This saves the model so be sure that is it valid
        person.picture.save(filename, File(lf))
        person.save()


    def make_party_membership(self,person,data):
        party,created = models.Party.objects.get_or_create(code=data[1],defaults={'name':data[0]})
        mem,c = models.PartyMembership.objects.get_or_create(
                person = person,
                party = party,
                start_date = import_utils.str_to_date(data[3]),
                end_date = import_utils.str_to_date(data[4]),
                )

    def make_pm(self,person,start=None,end=None):
        self.make_ministerial(person,"Prime Minister",start,end)

    def make_deputy_pm(self,person,start=None,end=None):
        self.make_ministerial(person,"Deputy Prime Minister",start,end)

    def make_opposition_leader(self,person,start=None,end=None):
        self.make_ministerial(person,"Leader of the Opposition",start,end)

    def make_ministerial(self,person,ministerialposition,start=None,end=None):
        ministerial_position,c = models.MinisterialPosition.objects.get_or_create(name=ministerialposition)
        models.MinisterialAppointment.objects.get_or_create(
            person=person,
            position=ministerial_position,
            start_date=start,
            end_date=end)