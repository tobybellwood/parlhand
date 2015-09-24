#from __future__ import print_function
import os, re, csv
from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError
from lxml import etree
from optparse import make_option

from parlhand.management.commands import utils as import_utils

class OutputManager():
    def __init__(self,filename,header):
        self.header = header
        self.filename = filename
        self.data = []
    def has(self,**kwargs):
        return self.get(**kwargs) is not False
    def append(self,row):
        self.data.append([row.get(col,'') for col in self.header])
    def add(self,row,check):
        checks = dict([(field,row[field]) for field in check])
        if not self.has(**checks):
            self.append(row)
            
    def get_as_dict(self,**kwargs):
        return dict(zip(self.header,self.get(**kwargs)))
        
    def get(self,_field=None,**kwargs):
        for field in kwargs.keys():
            if field not in self.header:
                return False
        checks = {}
        for field,value in kwargs.items():
            checks[self.header.index(field)] = value

        for d in self.data:
            if all([d[i]==value for i,value in checks.items()]):
                
                if _field is not None:
                    return d[self.header.index(_field)]
                return d
        return False


class Command(BaseCommand):
    args = 'xml_file_name'
    options = 'd'
    help = 'Import a  ParlBibXML file and create a new record or merge it with an existing record'

    option_list = BaseCommand.option_list + (
        make_option('-d','--dir',
            action='store',
            dest='dir',
            default='.',
            help='Output directory'),
        )

    def handle(self, *args, **options):
        self.output_files = {}
        self.output_files = {
            'committees': OutputManager('parlhand.committee.csv',['pk','name','type']),
            'committeememberships' : OutputManager(filename='parlhand.committeemembership.csv',
                header=['parlhand.person.phid','parlhand.committee.name','parlhand.committee.type','start_date','end_date','notes']
                ),
            'parties': OutputManager('parlhand.party.csv',['code','name','type']),
            'partymemberships' : OutputManager(filename='parlhand.partymembership.csv',
                header=['parlhand.person.phid','_name','parlhand.party.code','position','start_date','end_date','notes']
                )
            }

        for e,input_file in enumerate(args):
            if e % 10 == 0:
                print '.',
            self.process_xml_file(input_file)
        for d,e in self.output_files.items():
            filename = os.path.join(options['dir'],e.filename)
            with open(filename, 'w+') as csvfile:
                out = csv.writer(csvfile)
                out.writerow(e.header)
                for row in e.data:
                    out.writerow(row)

    def process_xml_file(self,file):
        #print("importing - ",file)
        with open(file, 'r') as imported_xml:
            self.parl_xml = etree.parse(imported_xml).xpath('/biog.entry')[0]

            self.phid = self.parl_xml.xpath('name.id')[0].text
            self.name = self.parl_xml.xpath('name')[0].text
            if self.phid is None or self.phid == "":
                raise Exception

            self.run(self.update_committees,'committee.service')
            self.run(self.update_party_positions,'party.positions')
            self.run(self.update_party_positions,'party.positions')
            #self.run(self.update_military,'military.service')

        #print("Done")

    def run(self,func,xpath,*args):
        elem = self.parl_xml.xpath(xpath)
        if len(elem) > 0:
            return func(self.phid,elem[0],*args)
    

    def update_committees(self,phid,committees):
        #print('Updating committee positions')
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
                comm_name = comm.split('from',1)[0].strip()
                try:
                    dates = "from"+comm.split('from',1)[1]
                except:
                    print '(',phid,'-',comm,')',
                    continue
                    #raise
                    
                # If you don't understand regular expressions, view the one below in https://regex101.com/ for a full breakdown
                # The short version is it finds most possible dates for a committee membership from relatively freetext string
                date_regex = "(?:from (?P<start>[\d\.]+)(?:(?P<notes>.*?)?(?: to (?P<end>[\d\.]+)))?)"
                
                dates = re.findall(date_regex,dates)
                committees = self.output_files['committees']
                committees.add({'pk':len(committees.data),'name':comm_name,'type':comm_type},check=('name','type'))
                committee = committees.get_as_dict(name=comm_name,type=comm_type)
                
                for date in dates:
                    start = date[0]
                    notes = date[1].strip()
                    end = date[2]
                    # For reference, this is the header:
                    # ['parlhand.person.phid','parlhand.committee.name','parlhand.committee.type',
                    #  'start_date','end_date','notes']
                    com_mem = self.output_files['committeememberships']
                    start_date = import_utils.str_to_date(start)
                    if start_date:
                        start_date = start_date.date()
                    end_date = import_utils.str_to_date(end)
                    if end_date:
                        end_date = end_date.date()
                    com_mem.append({
                        'parlhand.person.phid':phid,
                        'parlhand.committee.name':committee['name'],
                        'parlhand.committee.name':committee['type'],
                        'start_date':start_date,
                        'end_date':end_date,
                        'notes':notes,
                        })

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

                # ['parlhand.person.phid','_name','parlhand.party.code',
                #  'position','start_date','end_date']

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
