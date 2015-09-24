from __future__ import print_function
import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from parlhand import models

class Command(BaseCommand):
    args = ''
    help = 'Setup aus parl details'

    def handle(self, *args, **options):
        seat_types = [
            #(chamber,individual title,individual plural,jurisdiction code,description),
            ('Senate','Senator','Senators','Australia','Elected members of the Australian Senate'),
            ('House of Representatives','Member','Members','Australia','Elected members of the Australian House of Representatives'),
            ('Legislative Assembly (NSW)','Member of the Legislative Assembly (NSW)','Members of the Legislative Assembly (NSW)','NSW','Elected members of the New South Wales Legislative Assembly'),
            ('Legislative Council (NSW)','Member of the Legislative Council (NSW)','Members of the Legislative Council (NSW)','NSW','Elected members of the New South Wales Legislative Council'),
            ('Legislative Assembly (Vic)','Member of the Legislative Assembly (Vic)','Members of the Legislative Assembly (Vic)','VIC','Elected members of the Victorian Legislative Assembly'),
            ('Legislative Council (Vic)','Member of the Legislative Council (Vic)','Members of the Legislative Council (Vic)','VIC','Elected members of the Victorian Legislative Council'),
        ]
        