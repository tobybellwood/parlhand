from django.core.cache import cache
from django.db import models
from model_utils.models import TimeStampedModel
from model_utils import Choices
import datetime
from fields import ApproximateDateField
from django.core.urlresolvers import reverse

def senators():
#    return Person.objects.filter(service__seat_type=Service.SEAT_TYPES.Senator, service__end_date__isnull=True)
    return Person.objects.filter(service__seat_type=Service.SEAT_TYPES.Senator, service__end_date="")

def members():
    return Person.objects.filter(service__seat_type=Service.SEAT_TYPES.Member, service__end_date="")
#    return Person.objects.filter(service__seat_type=Service.SEAT_TYPES.Member, service__end_date__isnull=True)

class Person(TimeStampedModel):
    """
    A person of historical parliamentary interest.
    
    Each individual is given a unique 'Parliamentary ID' as well as a senator and member id, based on the order \
    they joined parliament. E.g. S100 is the 100th person to become a Senator, and H052 is the 52nd to become a Member.
    Where a person has been a Senator and a Member they will have both IDs assigned.
    If a person retires from the House and then recontests in a separate electorate they will retain their original IDs.
    """
    phid = models.CharField(max_length=200,unique=True,primary_key=True)
    sen_id = models.CharField(max_length=30, null=True, blank=True)
    rep_id = models.CharField(max_length=30, null=True, blank=True)

    honorifics = models.CharField(max_length=255, null=True, blank=True,help_text="Fancy term for things before someones name. E.g. 'Dr.'")
    first_names = models.CharField(max_length=255, null=True, blank=True)
    preferred_name = models.CharField(max_length=255, null=True, blank=True,
        help_text="A common or informal given name. E.g. 'Billy' as in William 'Billy' Hughes")
    surname = models.CharField(max_length=255)
    postnomials = models.CharField(max_length=255, null=True, blank=True,help_text="Fancy term for things after someones name. E.g. 'Ph.D.'")
    also_known_as = models.TextField(null=True, blank=True)

    biography = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, blank=True)
    
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, null=True, blank=True)
    place_of_death = models.CharField(max_length=255, null=True, blank=True)
    
    GENDER = Choices('Male', 'Female')
    gender = models.CharField(choices=GENDER, default=GENDER.Male, max_length=20)
    
    class Meta:
        verbose_name_plural="People"
        ordering = ['surname','first_names']
    
    def __str__(self):
        return "%s, %s (%s)"%(self.surname, self.first_names, self.preferred_name)
    
    def get_absolute_url(self):
        return reverse('parliamentarian', kwargs={'phid': self.phid})

    @property
    def full_name(self):
        return str(self)
    @property
    def length_of_service(self):
        key = "%s--days_served"%self.phid
        cached_days = cache.get(key) 
        if cached_days:
            return cached_days

        los = datetime.timedelta()
        for e in self.service_set.all():
            if e.start_date is None:
                return None
            elif e.end_date is None:
                start = e.start_date.early()
                los += datetime.datetime.today().date() - datetime.date(year=start.year,month=start.month,day=start.day)
            else:
                end = e.end_date.late()
                start = e.start_date.early()
                los += datetime.date(year=end.year,month=end.month,day=end.day) - datetime.date(year=start.year,month=start.month,day=start.day)
        cache.set(key, los, 24*60*60) # cache for a day
        return los

    def current_party(self):
        membership = self.partymembership_set.filter(end_date="").first()
        if membership is None:
            return membership
        else:
            return membership.party
    current_party.short_description = 'Current Party'

    def current_seat(self):
        return Service.objects.filter(person=self).filter(end_date="").first()
    current_seat.short_description = 'Current Seat'

    def person_type(self):
        seat = self.current_seat()
        if seat:
            return seat.seat_type
        else:
            return "Former parliamentarian"

    def committees(self):
        return self.committeemembership_set.order_by('committee__name')

    def first_event(self):
        return Service.objects.filter(person=self).filter(start_date__isnull=False).order_by('start_date').first()

class Group(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.name

class ElectionType(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    
class Election(models.Model):
    date = ApproximateDateField(null=True, blank=True,help_text="")
    person = models.ForeignKey(ElectionType)
    during_parliament = models.ForeignKey("Parliament",related_name="ffffff")

class Parliament(Group):
    number = models.IntegerField()
    start_election = models.ForeignKey(Election,related_name="started_parliament")
    end_election = models.ForeignKey(Election,related_name="ended_parliament",null=True, blank=True)

class CurrentEventQuerySet(models.QuerySet):
    def current(self):
        return self.filter(end_date="")

class Event(models.Model):
    objects  = CurrentEventQuerySet.as_manager()
    class Meta:
        abstract = True
        ordering = ['-end_date','-start_date']
    person = models.ForeignKey(Person)
    start_date = ApproximateDateField(null=True, blank=True,help_text="The date an event started.")
    end_date = ApproximateDateField(null=True, blank=True,help_text="The date an event finished. If an end date is not given and point_in_time is false the event is presumed to be ongoing.")
    point_in_time = models.BooleanField(default=True,help_text="Used to indicate an event was a singular point in time.")

class State(models.Model):
    """
    A recognised Australian State or Territory
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10,primary_key=True,help_text="3 letter code")
    def __str__(self):
        return self.code

class Electorate(models.Model):
    """
    An electorate for a federal election as defined by the Australian Electoral Commission.
    """
    name = models.CharField(max_length=200, null=True, blank=True)
    state = models.ForeignKey(State)
    description = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.name

class Service(Event):
    """
    Records a period of parliamentary service for an individual.
    Continuous holdings of an electorate across elections are considered a single period of service.
    """
    start_reason = models.CharField(max_length=200)
    end_reason = models.CharField(max_length=200, null=True, blank=True)
    parliament = models.ForeignKey(Parliament, blank=True, null=True)
    electorate = models.ForeignKey(Electorate)
    elections = models.ManyToManyField(Election)
    SEAT_TYPES = Choices('Senator', 'Member')
    seat_type = models.CharField(choices=SEAT_TYPES, default=SEAT_TYPES.Member, max_length=20,help_text="Defines a if the period of service was as a Senator or Member.")
    def __str__(self):
        return "%s" % (self.electorate.name)

class Party(Group):
    """
    An Australian political party that is (or has been) registered with the Australian Electoral Commission

    Parties are often branded with colours in both Party and AEC material, e.g. Labor is often associated with red.
    Here we can record colors for parties to be used in presentation where appropriate.
    Colours should be 'CSS" safe, eg. Hexidecimal or named HTML web colours.
    Note: Primary/Secondary may not always equate to Foreground/Background text colours during presentation,
    however colours should be readable when used as in this fashion.
    """
    code = models.CharField(max_length=10, primary_key=True)
    primary_colour = models.CharField(max_length=30,default="#FFF")
    secondary_colour = models.CharField(max_length=30,default="#000")
    class Meta:
        verbose_name_plural="Parties"
    def __str__(self):
        return self.name
        
class PartyMembership(Event):
    """
    The record of a persons membership within a political party.
    """
    party = models.ForeignKey(Party)

class MinisterialPosition(Group):
    """
    A named ministerial position, both Government and 'Shadow'.
    Commonly known as a 'Ministry' (e.g. Ministry of Health). We have renamed it to avoid confusion\
    with a Ministry (as belonging to a Prime Minister, containing many Ministers).
    """
    def get_absolute_url(self):
        return reverse('ministerialposition', kwargs={'mid': self.pk})
        

class Ministry(Group):
    """
    A ministry belonging to a Prime MinisterThe record of a persons membership within a political party.
    """
    number = models.IntegerField(unique=True,primary_key=True)
    parties = models.ManyToManyField(Party)
    start_date = ApproximateDateField(null=True, blank=True,help_text="The date an event started.")
    end_date = ApproximateDateField(null=True, blank=True,help_text="The date an event finished. If an end date is not given and point_in_time is false the event is presumed to be ongoing.")
    picture = models.ImageField(null=True, blank=True)
    class Meta:
        ordering = ['-end_date','-start_date']
        verbose_name_plural="Ministries"

class MinisterialAppointment(Event):
    """
    The record of an individual holding a ministerial position, and when they held it.
    A person may hold a ministerial position more than once.
    """
    position = models.ForeignKey(MinisterialPosition)
    ministry = models.ForeignKey(Ministry,null=True)
    TYPES = Choices(('Cabinet','Cabinet'),
                    ('Inner','Inner'),
                    ('Outer','Outer'),
                    ('Shadow','Shadow'),
                    ('ParlSec','Parliamentary Secretary'),)
    type = models.CharField(choices=TYPES, default=TYPES.Cabinet, max_length=20,
        help_text="The type of ministry position held - %s"%(', '.join([t[0] for t in TYPES]))
        )

class Committee(Group):
    """
    A named parliamentary committee.
    """
    type = models.CharField(max_length=200, null=True, blank=True)

class CommitteeMembership(Event):
    """
    The record of a person sitting on a committee.
    """
    committee = models.ForeignKey(Committee)
    notes = models.TextField()
    class Meta:
        # Changing this default ordering will mess with the display of committees in pages.
        # This is due to how Django does regrouping in templates.
        # Ye be warned - Sam Spencer.
        ordering = ['committee__type','committee__name','-end_date','-start_date']

class PartyPosition(Event):
    """
    The record of a person holding a non-parliamentary position with their political party.
    E.g. Regional secretary, party leader.
    """
    party = models.ForeignKey(Party)
    position = models.CharField(max_length=200, null=True, blank=True)

class ParliamentaryPosition(Event):
    """
    The record of a person holding a specific parliamentary position.
    E.g. Speaker, Deputy Speaker, President of the Senate.
    """
    position = models.CharField(max_length=200, null=True, blank=True)

class YearOnlyEvent(models.Model):
    class Meta:
        abstract = True
        ordering = ['-end_year','-start_year']
    person = models.ForeignKey(Person)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)

class MilitaryService(YearOnlyEvent):
    """
    A record of military service for a parliamentarian.
    """
    rank = models.CharField(max_length=200, null=True, blank=True)
    service = models.CharField(max_length=200, null=True, blank=True)
    unit = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

class Occupation(YearOnlyEvent):
    """
    A record of notable occupations for a parliamentarian, either before or after their service.
    Occupation Fields are derived from values in the Australian Bureau of Statistics\
    Australian and New Zealand Standard Classification of Occupations, 2013, Version 1.2.
    """
    title = models.CharField(max_length=200, null=True, blank=True)
    FIELDS = Choices(
    (1, "manager", "Managers"),
    (2, "professional", "Professionals"),
    (3, "technician", "Technicians and Trades Workers"),
    (4, "community", "Community and Personal Service Workers"),
    (5, "clerical", "Clerical and Administrative Workers"),
    (6, "sales", "Sales Workers"),
    (7, "operator", "Machinery Operators and Drivers"),
    (8, "labourer", "Labourers"),
    )
    field = models.CharField(choices=FIELDS, null=True, max_length=50)

class Qualification(models.Model):
    """
    A record of a notable qualification held by a parliamentarian.
    Education levels and fields are derived from values in the Australian Bureau of Statistics\
    Australian Standard Classification of Education (ASCED), 2001.
    """
    person = models.ForeignKey(Person)
    LEVELS = Choices(
        (1, 'postgraduate', "Postgraduate Degree Level"),
        (2, 'graduate', "Graduate Diploma and Graduate Certificate Level"),
        (3, 'bachelor', "Bachelor Degree Level"),
        (4, 'diploma', "Advanced Diploma and Diploma Level"),
        (5, 'certificate', "Certificate Level."),
        (6, 'secondary', "Secondary Education"),
        (7, 'primary', "Primary Education"),
        (8, 'preprimary', "Pre-primary Education"),
        (9, 'other', "Other Education"),
        (10, 'none', "No Formal Education"),
        )
    level = models.CharField(choices=LEVELS, null=True, max_length=50)
    FIELDS = Choices(
        (1, "science", "Natural and Physical Sciences"),
        (2, "it", "Information Technology"),
        (3, "engineering", "Engineering and Related Technologies"),
        (4, "architecture", "Architecture and Building"),
        (5, "agriculture", "Agriculture, Environmental and Related Studies"),
        (6, "health", "Health"),
        (7, "education", "Education"),
        (8, "management", "Management and Commerce"),
        (9, "society", "Society and Culture"),
        (10, "creative", "Creative Arts"),
        (11, "personal", "Food, Hospitality and Personal Services"),
        (12, "mixed", "Mixed Field Programmes.")
    )
    field = models.CharField(choices=FIELDS, null=True, max_length=50)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_awarded = models.DateField(null=True, blank=True)

class Honour(models.Model):
    person = models.ForeignKey(Person)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_awarded = models.DateField(null=True, blank=True)

class Publication(models.Model):
    """
    A publication of notable importance by a parliamentarian.
    """
    person = models.ForeignKey(Person)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    date_published = models.DateField(null=True, blank=True)

class ExternalReferenceLink(models.Model):
    """
    """
    person = models.ForeignKey(Person)
    url = models.URLField(max_length=200, null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
