from parlhand import models
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
import datetime
#from parlhand.templatetags.parl_utils import days_to_years
from data_interrogator import interrogation_room

def parliamentarian(request,phid):
    parl = get_object_or_404(models.Person, phid=phid)
    
    start_event = models.Service.objects.filter(person=parl).filter(start_date__isnull=False).order_by('start_date').first()
    if start_event is None:
        vis_start_date = parl.birth_date
    else:
        vis_start_date = start_event.start_date
    
    if parl.death_date:
        vis_end_date = parl.death_date
    else:
        active = models.Service.objects.filter(person=parl).filter(end_date__isnull=False).exists()
        vis_end_date = "2016"
        if False and active is True:
            vis_end_date = "2016"
        elif False:
            last_service = models.Service.objects.filter(person=parl).filter(end_date__isnull=False).order_by('-end_date').first()
            vis_end_date = last_service.end_date

    return render(request,"parlhand/parliamentarian.html",{
        "person":parl,
        'start_event':vis_start_date,
        'end_event':vis_end_date,
        })

def current_chamber(request,chamber):
    parliament = None
    title= None
    if chamber == "senate":
        parliamentarians = models.senators()
        title="Senator"
    elif chamber == "house":
        parliamentarians = models.members()
        title="Member"
    from django.db.models import Count
    import json
    party_breakdown = models.Party.objects.filter(partymembership__end_date__isnull=True,partymembership__person__service__end_date__isnull=True,partymembership__person__service__chamber__title=title).annotate(count=Count('partymembership__person',distinct=True)).values('name','code','primary_colour','count').distinct()
    
    party_breakdown = [dict(**i) for i in party_breakdown]
    return render(request,"parlhand/current/%s.html"%chamber,
        {"parliamentarians":parliamentarians,"parliament":parliament, "breakdown":json.dumps(party_breakdown)})

def all_parliamentarians(request):
    parliamentarians = models.Person.objects.all()

    return render(request,"parlhand/tables/all_past.html",{"parliamentarians":parliamentarians})

def ministerialposition(request,mid):
    ministerialposition = get_object_or_404(models.MinisterialPosition, id=mid)
    return render(request,"parlhand/stuff/ministerialposition.html",{"ministerialposition":ministerialposition})

def ministry(request,ministry_number):
    ministry = get_object_or_404(models.Ministry, number=ministry_number)
    ministry_number=int(ministry_number)
    
    ministers = ministry.ministerialappointment_set.order_by("person__family_name","start_date","end_date").all()
    concurrent_ministry_data = {}
    for m in ministers:
        start = str(m.start_date)
        end = str(m.end_date)
        key = (m.person,str(m.role),start,end)
        mins = concurrent_ministry_data.get(key,[]) +[m.position.label]
        concurrent_ministry_data[key] = mins

    base_query = ministry.ministerialappointment_set.order_by('position__label','start_date','end_date')

    context = {
        "ministry": ministry,
        "ministers":ministers,
        "later_ministry":models.Ministry.objects.filter(number=ministry_number+1).first(),
        "prior_ministry":models.Ministry.objects.filter(number=ministry_number-1).first(),
        "cabinet": base_query.filter(role="Cabinet"),
        "outer": base_query.filter(role=""),
        "parlsec": base_query.filter(role="Parliamentary Secretary"),
        "concurrent_ministry_data":concurrent_ministry_data
        }
    return render(request,"parlhand/stuff/ministry.html",context)

def electorate(request,eid):
    electorate = get_object_or_404(models.Electorate, id=eid)

    return render(request,"parlhand/stuff/electorate.html",{"electorate":electorate})

def party(request,code):
    party = get_object_or_404(models.Party, code=code)
    return render(request,"parlhand/stuff/party.html",{"party":party})

def parliament(request,number):
    parliament = get_object_or_404(models.Parliament, number=number)
    return render(request,"parlhand/stuff/parliament.html",{"parliament":parliament})

def committee(request,cid):
    committee = get_object_or_404(models.Committee, pk=cid)
    return render(request,"parlhand/stuff/committee.html",{"committee":committee})

def custom_table(request):
    return interrogation_room(request,template='parlhand/tables/custom.html')

def dynamic_css(request,name):
    model = {'party':models.Party}.get(name)
    objs = model.objects.all()
    try:
        return render(request,"parlhand/dyncss/%s.css"%name,{'objs':objs},content_type='text/css')
    except:
        return ""

def on_this_day(request,month=None,day=None):
    if month is None or day is None:
        date = datetime.date.today()
        day = date.day
        month = date.month
        year = date.year
    day = int(day)
    month = int(month)
    
    # we need this to pretty print the date in the template.
    date = datetime.date(year = datetime.date.today().year, month=month, day=day) 
    
    #template = _date__month=month,_date__day=day,_confidence='YYYY-MM-DD'
    
    births = models.Person.objects.filter(birth_date__month=month,birth_date__day=day,birth_confidence='YYYY-MM-DD')
    service_starts = models.Service.objects.filter(start_date__month=month,start_date__day=day,start_confidence='YYYY-MM-DD')
    service_ends = models.Service.objects.filter(end_date__month=month,end_date__day=day,end_confidence='YYYY-MM-DD')

    ministry_starts = models.MinisterialAppointment.objects.filter(start_date__month=month,start_date__day=day,start_confidence='YYYY-MM-DD')
    ministry_ends = models.MinisterialAppointment.objects.filter(end_date__month=month,end_date__day=day,end_confidence='YYYY-MM-DD')

    return render(request,"parlhand/on_this_day.html",{
        'date':date,
        'day':day,
        'month':month,
        "births":births,
        "service_starts":service_starts,
        "service_ends":service_ends,
        "ministry_starts":ministry_starts,
        "ministry_ends":ministry_ends,
        })

from haystack.generic_views import SearchView
from parlhand.forms.search import SpellingSearchQuerySet, SpellingSearchForm

class ParliamentSearchView(SearchView):
    form_class = SpellingSearchForm
    queryset = SpellingSearchQuerySet()
