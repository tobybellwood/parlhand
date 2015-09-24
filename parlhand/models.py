from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils import Choices
import datetime
from parlhand.popolo import models as popolo
from parlhand import pages # needed to pull feincms in!
from parlhand.fields import ApproximateDateField

def senators():
    #return Person.objects.filter(service__chamber__title='Senator', service__end_date="")
    return Person.objects.filter(service__chamber__title='Senator', service__end_date__isnull=True)
def members():
    #return Person.objects.filter(service__chamber__title='Member', service__end_date="")
    return Person.objects.filter(service__chamber__title='Member', service__end_date__isnull=True)

class Person(popolo.Person):
    """
    A person of historical parliamentary interest.
    
    Each individual is given a unique 'Parliamentary ID' as well as a senator and member id, based on the order \
    they joined parliament. E.g. S100 is the 100th person to become a Senator, and H052 is the 52nd to become a Member.
    Where a person has been a Senator and a Member they will have both IDs assigned.
    If a person retires from the House and then recontests in a separate electorate they will retain their original IDs.
    """
    phid = models.CharField(max_length=200,unique=True,primary_key=True)
    sen_id = models.CharField(max_length=30, null=True, blank=True) # Better modeled as popolo.Identifier
    rep_id = models.CharField(max_length=30, null=True, blank=True) # Better modeled as popolo.Identifier

    #honorifics = models.CharField(max_length=255, null=True, blank=True,help_text="Fancy term for things before someones name. E.g. 'Dr.'")
    #postnomials = models.CharField(max_length=255, null=True, blank=True,help_text="Fancy term for things after someones name. E.g. 'Ph.D.'")
    
    place_of_birth = models.CharField(max_length=255, null=True, blank=True)
    place_of_death = models.CharField(max_length=255, null=True, blank=True)
    #length_of_service = models.IntegerField(null=True, blank=True)
    
    def get_absolute_url(self):
        return reverse('parlhand:parliamentarian', kwargs={'phid': self.phid})

    
    def length_of_service(self):
        los = datetime.timedelta()
        for e in self.service_set.all():
            if e.start_date is None:
                return None
            elif e.end_date is None:
                #start = e.start_date.early()
                los += datetime.datetime.today().date() - e.start_date
            else:
                #end = e.end_date.late()
                #start = e.start_date.early()
                los += e.end_date - e.start_date #datetime.date(year=end.year,month=end.month,day=end.day) - datetime.date(year=start.year,month=start.month,day=start.day)
        return los

    def __str__(self):
        return '<%s> %s'%(self.phid,self.name)
    def current_seat(self):
        #return Service.objects.filter(person=self).filter(end_date="").first()
        return Service.objects.filter(person=self).filter(end_date__isnull=True).first()
    current_seat.short_description = 'Current Seat'
    def current_party(self):
        #memb = PartyMembership.objects.filter(person=self).filter(end_date="").first()
        memb = PartyMembership.objects.filter(person=self).filter(end_date__isnull=True).first()
        if memb is not None:
            return memb.party
        else:
            return 'None'

    @property
    def full_name(self):
        return ' '.join([self.given_name,self.additional_name,self.family_name])
    
class Membership(popolo.Membership):
    person = models.ForeignKey(Person)
    class Meta:
        abstract = True

class Party(popolo.Organization):
    """
    An Australian political party that is (or has been) registered with the Australian Electoral Commission

    Parties are often branded with colours in both Party and AEC material, e.g. Labor is often associated with red.
    Here we can record colors for parties to be used in presentation where appropriate.
    Colours should be "CSS" safe, eg. Hexidecimal or named HTML web colours.
    Note: Primary/Secondary may not always equate to Foreground/Background text colours during presentation,
    however colours should be readable when used as in this fashion.
    """
    class Meta:
        verbose_name_plural="Parties"
    code = models.CharField(max_length=10, primary_key=True)
    primary_colour = models.CharField(max_length=30,default="#FFF")
    secondary_colour = models.CharField(max_length=30,default="#000")
    descendent = models.ForeignKey("Party",null=True, blank=True)
    organization_type = "library.dps.gov.au/parlhand/#party"
    
    def get_absolute_url(self):
        return reverse('parlhand:party', kwargs={'code': self.code})

class PartyMembership(Membership):
    """
    The record of a persons membership within a political party.
    """
    organization_field = 'party'
    post_field = None
    party = models.ForeignKey(Party)

#class PartyPost(popolo.Post):
#    post_type = "library.dps.gov.au/parlhand/#party_position"

class PartyPosition(Membership):
    organization_field = 'party'
    #post_field = 'post'
    #post = models.ForeignKey(PartyPost)
    party = models.ForeignKey(Party)
    position = models.CharField(max_length=1024)

class Electorate(popolo.Post):
    """
    An electorate for a federal election as defined by the Australian Electoral Commission.
    """
    post_type = "library.dps.gov.au/parlhand/#electorate"

class Chamber(popolo.Organization):
    """
    An chamber of elected officials. Eg. Senate, House of Representatives, Legislative Assembly, etc...
    """
    organization_type = "library.dps.gov.au/parlhand/#chamber"
    title = models.CharField(_("title"), max_length=128, blank=True, help_text=_("The title of people within this chamber. E.g. Senator, Member, Lord, etc..."))
    level = models.CharField(null=True, blank=True, max_length=256)

class Service(Membership):
    """
    Records a period of parliamentary service for an individual.
    Continuous holdings of an electorate across elections are considered a single period of service.
    """
    start_reason = models.CharField(max_length=1024)
    end_reason = models.CharField(max_length=1024, null=True, blank=True)
    #parliament = models.ForeignKey(Parliament, blank=True, null=True)
    #elections = models.ManyToManyField(Election)
    
    def __str__(self):
        return "%s" % (self.electorate.label)

    chamber = models.ForeignKey(Chamber)
    electorate = models.ForeignKey(Electorate)
    post_field = 'electorate'
    organization_field = 'chamber'

    @property
    def seat_type(self):
        return self.chamber.title or None

class Area(popolo.Area):
    pass

class Ministry(popolo.Organization):
    """
    A ministry belonging to a Prime Minister.
    """
    class Meta:
        ordering = ['number']
        verbose_name_plural="ministries"
    organization_type = "library.dps.gov.au/parlhand/#ministry"
    number = models.IntegerField(unique=True,primary_key=True)
    def get_absolute_url(self):
        return reverse('parlhand:ministry', kwargs={'ministry_number': self.number})

    @property
    def prime_minister(self):
        return self.ministerialappointment_set.get(position__label="Prime Minister").person


class ChamberPosition(popolo.Post):
    """
    A named position, in service of a chamber of parliament.
    For example, Speaker of the House of Representatives, President of the Senate, etc.
    """
    post_type = "library.dps.gov.au/parlhand/#chamberposition"
    def get_absolute_url(self):
        return '' #reverse('parlhand:ministerialposition', kwargs={'mid': self.pk})


class ChamberAppointment(Membership):
    """
    The record of an individual holding a position within a chamber, and when they held it.
    """
    post_field = 'position'
    organization_field = 'chamber'
    on_behalf_of_field = 'party'
    position = models.ForeignKey(ChamberPosition)
    chamber = models.ForeignKey(Chamber)
    party = models.ForeignKey(Party,blank=True,null=True)

    def __unicode__(self):
        return '%s - %s: %s - %s'%(self.person.name,self.position.label,self.start_date,self.end_date)

class MinisterialPosition(popolo.Post):
    """
    A named ministerial position, both Government and 'Shadow'.
    Commonly known as a 'Ministry' (e.g. Ministry of Health). We have renamed it to avoid confusion\
    with a Ministry (as belonging to a Prime Minister, containing many Ministers).
    """
    post_type = "library.dps.gov.au/parlhand/#ministerialposition"
    def get_absolute_url(self):
        return reverse('parlhand:ministerialposition', kwargs={'mid': self.pk})


class MinisterialAppointment(Membership):
    """
    The record of an individual holding a ministerial position, and when they held it.
    A person may hold a ministerial position more than once.
    """
    post_field = 'position'
    organization_field = 'ministry'
    on_behalf_of_field = 'party'
    position = models.ForeignKey(MinisterialPosition)
    ministry = models.ForeignKey(Ministry)
    party = models.ForeignKey(Party,blank=True,null=True)

    def __unicode__(self):
        return '%s - %s: %s - %s'%(self.person.name,self.position.label,self.start_date,self.end_date)

class Addendum(models.Model):
    """
    Captures additional notes and relationships between persons.
    """
    people = models.ManyToManyField(Person)
    type = models.CharField(max_length=256,null=True, blank=True)
    date = ApproximateDateField(null=True, blank=True)
    start_date = ApproximateDateField(null=True, blank=True,help_text="The date an event started. To mark an event as a single point, set the start and end dates to be the same.")
    end_date = ApproximateDateField(null=True, blank=True,help_text="The date an event finished. If an end date is not given the event is presumed to be still active.")
    description = models.TextField()
    url = models.URLField(_("url"), max_length=350, help_text=_("A URL relating to this additional note or event"))
    
class Committee(popolo.Organization):
    """
    A named parliamentary committee.
    """
    type = models.CharField(max_length=256, null=True, blank=True)
    organization_type = "library.dps.gov.au/parlhand/#committee"
    def get_absolute_url(self):
        return reverse('parlhand:committee', kwargs={'cid': self.pk})

class CommitteeMembership(Membership):
    """
    The record of a person sitting on a committee.
    """
    notes = models.TextField()
    class Meta:
        # Changing this default ordering will mess with the display of committees in pages.
        # This is due to how Django does regrouping in templates.
        # Ye be warned - Sam Spencer.
        ordering = ['committee__type','committee__name','-end_date','-start_date']
        
    organization_field = 'committee'
    committee = models.ForeignKey(Committee)

class MilitaryBranch(popolo.Organization):
    """
    Army, Navy, Air Force, etc...
    """
    organization_type = "library.dps.gov.au/parlhand/#militarybranch"
    code = models.CharField(max_length=16, null=True, blank=True)

class MilitaryService(Membership):
    """
    A record of military service for a parliamentarian.
    """
    organization_field = 'branch'
    branch = models.ForeignKey(MilitaryBranch)
    unit = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

class Parliament(popolo.Organization):
    """
    Army, Navy, Air Force, etc...
    """
    organization_type = "library.dps.gov.au/parlhand/#parliament"
    number = models.IntegerField(unique=True,primary_key=True)
    election_date = ApproximateDateField(null=True, blank=True,help_text="The date of the election that led to this parliament.")

class StatutoryPosition(popolo.Post):
    """
    A named Statutory position
    """
    post_type = "library.dps.gov.au/parlhand/#statutoryposition"
    #def get_absolute_url(self):
    #    return reverse('parlhand:statutoryposition', kwargs={'mid': self.pk})


class StatutoryAppointment(Membership):
    """
    The record of an individual holding a Statutory position, and when they held it.
    A person may hold a Statutory position more than once.
    """
    post_field = 'position'
    position = models.ForeignKey(StatutoryPosition)
