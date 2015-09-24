from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

import models

class PersonAssociatedInline(admin.TabularInline):
    extra = 0

class EventInline(PersonAssociatedInline):
    pass

class PublicationInline(PersonAssociatedInline):
    model = models.Publication

class PartyMembershipInline(EventInline):
    model = models.PartyMembership

class ServiceInline(EventInline):
    model = models.Service

class ExternalReferenceLinkInline(admin.TabularInline):
    model = models.ExternalReferenceLink

class MinisterialAppointmentInline(EventInline):
    model = models.MinisterialAppointment
class CommitteeMembershipInline(EventInline):
    model = models.CommitteeMembership
class MilitaryServiceInline(EventInline):
    model = models.MilitaryService
class ParliamentaryPositionInline(EventInline):
    model = models.ParliamentaryPosition
class PartyPositionInline(EventInline):
    model = models.PartyPosition
class QualificationInline(PersonAssociatedInline):
    model = models.Qualification
class OccupationInline(EventInline):
    model = models.Occupation
class HonourInline(PersonAssociatedInline):
    model = models.Honour
    
class IsCurrentListFilter(admin.SimpleListFilter):
    title = 'Restricted Members:'
    parameter_name = 'is_current'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [ ('s','Current Senator'),('m','Current Member'),('f','Former parliamentarian')]


    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() in ['s','m']:
            if self.value() == 's':
                seat_type = models.Service.SEAT_TYPES.Senator
            if self.value() == 'm':
                seat_type = models.Service.SEAT_TYPES.Member
            queryset = queryset.filter(service__end_date__isnull=True,service__seat_type=seat_type)
        elif self.value() == 'f':
            queryset = queryset.filter(service__end_date__isnull=False)
        else:
            return queryset.all()
        return queryset

class CurrentPartyMembershipListFilter(admin.SimpleListFilter):
    title = 'Current Party'
    parameter_name = 'cur_par'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [ (p.code,"%s (%s)"%(p.name,p.code)) for p in models.Party.objects.all()]


    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is None:
            return queryset.all()
        return queryset.filter(partymembership__party__code=self.value(),partymembership__end_date__isnull=True)

class PersonModelAdmin(CompareVersionAdmin):
    list_display = ('phid', 'sen_id','rep_id','surname','first_names','preferred_name','date_of_birth','current_party','current_seat')
    search_fields = ['phid','first_names','preferred_name','surname']
    list_filter = [CurrentPartyMembershipListFilter] #[IsCurrentListFilter,CurrentPartyMembershipListFilter]
    
    inlines = [ 
                PartyMembershipInline,
                ServiceInline,
            ]+sorted([
                MinisterialAppointmentInline,
                CommitteeMembershipInline,
                MilitaryServiceInline,
                ParliamentaryPositionInline,
                PartyPositionInline,
                QualificationInline,
                OccupationInline
            ],key=lambda x:x.__name__)


admin.site.register(models.Person,PersonModelAdmin)

admin.site.register(models.Committee,CompareVersionAdmin)
admin.site.register(models.Electorate,CompareVersionAdmin)
admin.site.register(models.MinisterialPosition,CompareVersionAdmin)
admin.site.register(models.Ministry,CompareVersionAdmin)
admin.site.register(models.Parliament,CompareVersionAdmin)
admin.site.register(models.Party,CompareVersionAdmin)
admin.site.register(models.State,CompareVersionAdmin)
