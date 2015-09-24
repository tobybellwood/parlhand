"""
We tried and failed to get django-popolo to work. But couldn't. So we're replicating the bits we like here.
"""    
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
#from django.contrib.gis.db import models as gis
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel

from parlhand.fields import ApproximateDateField, ConfidenceDate

@python_2_unicode_compatible
class Person(TimeStampedModel):
    """
    A real person, alive or dead
    see schema at http://popoloproject.com/schemas/person.json#
    """
    class Meta:
        ordering = ['family_name','given_name']
        abstract = True

    GENDER = Choices('Male', 'Female')

    name = models.CharField(_("name"), max_length=512, help_text=_("A person's preferred full name"))
    family_name = models.CharField(_("family name"), max_length=128, blank=True, help_text=_("One or more family names"))
    given_name = models.CharField(_("given name"), max_length=128, blank=True, help_text=_("One or more primary given names"))
    additional_name = models.CharField(_("additional name"), max_length=128, blank=True, help_text=_("One or more secondary given names"))
    honorific_prefix = models.CharField(_("honorific prefix"), max_length=128, blank=True, help_text=_("One or more honorifics preceding a person's name"))
    honorific_suffix = models.CharField(_("honorific suffix"), max_length=128, blank=True, help_text=_("One or more honorifics following a person's name"))
    image = models.ImageField(null=True, blank=True, help_text=_("An image to identify the person visually"))
    gender = models.CharField(choices=GENDER, default=GENDER.Male, max_length=20)
    birth = ConfidenceDate(help_text=_("A date of birth"))
        #_("birth date"), null=True, blank=True, help_text=_("A date of birth"))
    death = ConfidenceDate(help_text=_("A date of death"))
        #_("death date"), null=True, blank=True, help_text=_("A date of death"))
    
    summary = models.CharField(_("summary"), max_length=1024, blank=True, help_text=_("A one-line account of a person's life"))
    biography = models.TextField(_("biography"), blank=True, help_text=_("An extended account of a person's life"))

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = generic.GenericRelation('Link', help_text="URLs to documents related to the person")

    # array of items referencing "http://popoloproject.com/schemas/other_name.json#"
    other_names = generic.GenericRelation('OtherName', help_text="Alternate or former names")

    # array of items referencing "http://popoloproject.com/schemas/identifier.json#"
    identifiers = generic.GenericRelation('Identifier', help_text="Issued identifiers")

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Organization(TimeStampedModel):
    """
    A group with a common purpose or reason for existence that goes beyond the set of people belonging to it
    see schema at http://popoloproject.com/schemas/organization.json#
    """
    class Meta:
        abstract = True
    organization_type = None

    name = models.CharField(_("name"), max_length=512, help_text=_("A primary name, e.g. a legally recognized name"))
    summary = models.CharField(_("summary"), max_length=1024, blank=True, help_text=_("A one-line description of an organization"))
    description = models.TextField(_("biography"), blank=True, help_text=_("An extended description of an organization"))

    # array of items referencing "http://popoloproject.com/schemas/other_name.json#"
    #other_names = generic.GenericRelation('OtherName', help_text="Alternate or former names")

    # array of items referencing "http://popoloproject.com/schemas/identifier.json#"
    #identifiers = generic.GenericRelation('Identifier', help_text="Issued identifiers")
    #classification = models.CharField(_("classification"), max_length=512, blank=True, help_text=_("An organization category, e.g. committee"))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
                               help_text=_("The organization that contains this organization"))

    # reference to "http://popoloproject.com/schemas/area.json#"
    # We explicitly DON'T define area here, each membership can specify if it has an area.
    #area = models.ForeignKey('Area', blank=True, null=True, related_name='organizations',
    #                           help_text=_("The geographic area to which this organization is related"))

    founding_date = ApproximateDateField(null=True, blank=True,help_text=_("A date of founding"))
    dissolution_date = ApproximateDateField(null=True, blank=True,help_text=_("A date of dissolution"))
    
    image = models.ImageField(null=True, blank=True, help_text=_("A URL of an image, to identify the organization visually"))

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = generic.GenericRelation('Link', help_text="URLs to documents about the organization")

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Post(TimeStampedModel):
    """
    A position that exists independent of the person holding it
    see schema at http://popoloproject.com/schemas/json#
    """
    class Meta:
        abstract = True
    post_type = None
    label = models.CharField(_("label"), max_length=512, blank=True, help_text=_("A label describing the post"))
    role = models.CharField(_("role"), max_length=512, blank=True, help_text=_("The function that the holder of the post fulfills"))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    # We explicitly DON'T define the organization here, each membership can specify exactly which organization types it has.
    #organization = models.ForeignKey('Organization', related_name='posts', help_text=_("The organization in which the post is held"))

    # reference to "http://popoloproject.com/schemas/area.json#"
    # We explicitly DON'T define area here, each membership can specify if it has an area.
    #area = models.ForeignKey('Area', blank=True, null=True, related_name='posts',
    #                           help_text=_("The geographic area to which the post is related"))

    def __str__(self):
        return self.label
        
class Membership(models.Model):
    """
    A relationship between a person and an organization
    see schema at http://popoloproject.com/schemas/membership.json#
    """
    class Meta:
        abstract = True

    #start_date = ApproximateDateField(null=True, blank=True,help_text=_("The date on which the relationship began"))
    start = ConfidenceDate()
    #end_date = ApproximateDateField(null=True, blank=True,help_text=_("The date on which the relationship ended"))
    end = ConfidenceDate()
    label = models.CharField(_("label"), max_length=512, blank=True, help_text=_("A label describing the membership"))
    role = models.CharField(_("role"), max_length=512, blank=True, help_text=_("The role that the person fulfills in the organization"))

    # We explicitly DON'T define the organization/person/post here, each membership can specify their own form or subclass of these.
    # reference to "http://popoloproject.com/schemas/person.json#"
    #person = models.ForeignKey('Person', to_field="id", related_name='memberships', help_text=_("The person who is a party to the relationship"))
    person_field = "person"

    # reference to "http://popoloproject.com/schemas/organization.json#"
    #organization = models.ForeignKey('Organization', blank=True, null=True, help_text=_("The organization that is a party to the relationship"))
    organization_field = None
    @property
    def organization(self):
        if self.organization_field:
            return getattr(self,self.organization_field).pk
        else:
            return None

    # reference to "http://popoloproject.com/schemas/post.json#"
    #post = models.ForeignKey('Post', blank=True, null=True, related_name='memberships',help_text=_("The post held by the person in the organization through this membership"))
    post_field = None
    @property
    def post(self):
        if self.post_field:
            return getattr(self,self.post_field).pk
        else:
            return None

    # reference to "http://popoloproject.com/schemas/organization.json#"
    on_behalf_of_field = None
    @property
    def on_behalf_of(self):
        if self.on_behalf_of_field:
            return getattr(self,self.on_behalf_of_field).pk
        else:
            return None


@python_2_unicode_compatible
class Area(TimeStampedModel):
    """
    An area is a geographic area whose geometry may change over time.
    see schema at http://popoloproject.com/schemas/area.json#
    """
    class Meta:
        abstract = True

    name = models.CharField(_("name"), max_length=256, blank=True, help_text=_("A primary name"))
    identifier = models.CharField(_("identifier"), max_length=512, blank=True, help_text=_("An issued identifier"))
    classification = models.CharField(_("identifier"), max_length=512, blank=True, help_text=_("An area category, e.g. city"))

    # reference to "http://popoloproject.com/schemas/area.json#"
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
                               help_text=_("The area that contains this area"))

    # geom property, as text (GeoJson, KML, GML)
    # We will be changing this to a proper GeoField in the future!
    geom = models.TextField(_("geom"), null=True, blank=True, help_text=_("A geometry"))
    #geom = gis.PolygonField(_("geom"), null=True, blank=True, help_text=_("A geometry"))

    # inhabitants, can be useful for some queries
    inhabitants = models.IntegerField(_("inhabitants"), null=True, blank=True, help_text=_("The total number of inhabitants"))

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = generic.GenericRelation('Source', blank=True, null=True, help_text="URLs to source documents about the area")

    def __str__(self):
        return self.name


class GenericRelatable(models.Model):
    """
    An abstract class that provides the possibility of generic relations
    """
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.CharField(blank=True, null=True, max_length=256)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


@python_2_unicode_compatible
class OtherName(GenericRelatable):
    """
    An alternate or former name
    see schema at http://popoloproject.com/schemas/name-component.json#
    """
    name = models.CharField(_("name"), max_length=512, help_text=_("An alternate or former name"))
    note = models.CharField(_("note"), max_length=1024, blank=True, help_text=_("A note, e.g. 'Birth name'"))
    start_date = ApproximateDateField(null=True, blank=True,help_text=_("The date on which the name was adopted"))
    end_date = ApproximateDateField(null=True, blank=True,help_text=_("The date on which the name was abandoned"))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Identifier(GenericRelatable):
    """
    An issued identifier
    see schema at http://popoloproject.com/schemas/identifier.json#
    """
    identifier = models.CharField(_("identifier"), max_length=512, help_text=_("An issued identifier, e.g. a DUNS number"))
    scheme = models.CharField(_("scheme"), max_length=128, blank=True, help_text=_("An identifier scheme, e.g. DUNS"))

    def __str__(self):
        return "{0}: {1}".format(self.scheme, self.identifier)


@python_2_unicode_compatible
class Link(GenericRelatable):
    """
    A URL
    see schema at http://popoloproject.com/schemas/link.json#
    """
    url = models.URLField(_("url"), max_length=350, help_text=_("A URL"))
    note = models.CharField(_("note"), max_length=512, blank=True, help_text=_("A note, e.g. 'Wikipedia page'"))

    def __str__(self):
        return self.url

