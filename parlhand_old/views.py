import models
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from parlhand.templatetags.parl_utils import days_to_years
from data_interrogator import interrogation_room

def parliamentarian(request,phid):
    parl = get_object_or_404(models.Person, phid=phid)
    
    start_event = models.Service.objects.filter(person=parl).filter(start_date__isnull=False).order_by('start_date').first()
    if start_event is None:
        vis_start_date = parl.birth_date
    else:
        vis_start_date = start_event.start_date
    print vis_start_date

    return render(request,"parlhand/parliamentarian.html",{
        "person":parl,
        'start_event':vis_start_date,
        })

def current(request,chamber,phid):
    parl = get_object_or_404(models.Person, phid=phid)
    if parl.current_seat().seat_type.lower() != seat_type:
        pass #redirect
    seat_type = {'senate':'Senator','house':'Member'}.get(chamber)
    if parl.current_seat().seat_type == models.Service.SEAT_TYPES.Senator:
        house = "Senate"
    elif  parl.current_seat().seat_type == models.Service.SEAT_TYPES.Member:
        house = "House of Representatives"
    return render(request,"parlhand/current_parliamentarian.html",{"person":parl,"house":house})

def home(request):
    return render(request,"parlhand/home.html")
    
# Displays all current senators and members on a single page.
def all_current(request):
    return render(request,"parlhand/all_current.html",
        {"senators":models.senators(),"members":models.members()})

def current_ministry(request):
    pass

def current_chamber(request,chamber):
    parliament = None
    if chamber == "senate":
        parliamentarians = models.senators()
    elif chamber == "house":
        parliamentarians = models.members()
    return render(request,"parlhand/current/%s.html"%chamber,
        {"parliamentarians":parliamentarians,"parliament":parliament})

def women_in_parliament(request):
    parliamentarians = models.Person.objects.filter(gender=models.Person.GENDER.Female)
    key_dates = []
    ""
    fevents = models.Service.objects.filter(person__gender=models.Person.GENDER.Female)
    from datetime import timedelta, date
    for seat in [models.Service.SEAT_TYPES.Member,models.Service.SEAT_TYPES.Senator]:
        key_dates_m = {}
        for e in fevents.filter(seat_type=seat).order_by("start_date"):
            events = models.Service.objects.filter(person__gender=models.Person.GENDER.Female).filter(seat_type=seat)
            if e.start_date and e.start_date not in key_dates_m.keys():
                #print type(e.start_date)
                query = Q(start_date__lte=e.start_date) & (Q(end_date__gte= e.start_date) | Q(end_date=""))
                #key_dates_m[e.start_date]=[events.filter(query).count(),'Member']
                day_before = e.start_date.date() - timedelta(days=1)
                #print type(day_before)
                query = Q(start_date__lte=day_before) & (Q(end_date__gte= day_before) | Q(end_date=""))
                key_dates_m[day_before]=[events.filter(query).count(),seat]
                day_after = e.start_date.date() + timedelta(days=1)
                #print type(day_after)
                query = Q(start_date__lte=day_after) & (Q(end_date__gte= day_after) | Q(end_date=""))
                key_dates_m[day_after]=[events.filter(query).count(),seat]
            if e.end_date and e.end_date not in key_dates_m.keys():
                day_before = e.end_date.date() - timedelta(days=1)
                #print type(day_before)
                query = Q(start_date__lte=day_before) & (Q(end_date__gte= day_before) | Q(end_date=""))
                key_dates_m[day_before]=[events.filter(query).count(),seat]
                #print type(e.end_date)
                query = Q(start_date__lte=e.end_date) & (Q(end_date__gte= e.end_date) | Q(end_date=""))
                #key_dates_m[e.end_date]=[events.filter(query).count(),'Member']
                day_after = e.end_date.date() + timedelta(days=1)
                #print type(day_after)
                query = Q(start_date__lte=day_after) & (Q(end_date__gte= day_after) | Q(end_date=""))
                key_dates_m[day_after]=[events.filter(query).count(),seat]
        today = date.today()
        if today not in key_dates_m.keys():
            query = Q(end_date="")
            key_dates_m[today]=[events.filter(query).count(),seat]
        key_dates = key_dates + [[date]+counts for date,counts in key_dates_m.items()]
    #key_dates = [[date]+counts for date,counts in key_dates_m.items()+key_dates_s.items()]
    ""
    return render(request,"parlhand/topics/women_in_parliament.html",
        {"parliamentarians":parliamentarians,'dates':key_dates})

from django.http import JsonResponse
from django.db.models import Count
def events_api(request):
    aggregators = request.GET.getlist('aggregator',['seat_type'])
    since = request.GET.get('since','1900-01-01')
    filters = request.GET.getlist('filter',[])
    fils = {}
    for f in filters:
        fil,val = f.split('|')
        fils[fil]=val
    event_type = models.Service.objects
    events = event_type.filter(start_date__gt=since).filter(**fils)
    
    from datetime import timedelta, date

    available_keys = []
    candidate_keys = event_type.values(*aggregators).order_by().distinct()
    for k in candidate_keys:
        available_keys.append('-'.join([k[agg] for agg in aggregators]))

    #def get_date_data_for_query(ds,events,query,query_date,aggregators,available_keys):
    ds = key_dates = {}
    def get_date_data_for_query(query,query_date):
        # We call this in two places and only within this function, and it needs to modify a ton of local stuff
        # So a local function with 2 arguments is a better pattern than a module function with the 7 or so arguments.
        val = events.filter(query).values(*aggregators).order_by().annotate(*[Count(a) for a in aggregators])
        for v in val:
            agg_var = "-".join([str(v[x]) for x in aggregators])
            if not ds.get(agg_var,None):
                ds[agg_var]={'keys':None,'data':{}}
            if ds[agg_var]['keys'] is None:
                ds[agg_var]['keys'] = [(x,v[x]) for x in aggregators]
            if str(query_date) not in ds[agg_var]['data']:
                ds[agg_var]['data'][str(query_date)] = int(v[aggregators[0]+'__count'])
        for k in available_keys:
            if not ds.get(k,None):
                ds[k]={'keys':None,'data':{}}
            if str(query_date) not in ds[k]['data']:
                ds[k]['data'][str(query_date)] = 0
    
    for e in events.order_by("start_date"):
        for event_date in [e.start_date,e.end_date]:
            if event_date:
                day_after = event_date.date() + timedelta(days=1)
                day_before = event_date.date() - timedelta(days=1)
                for query_date in [day_before,day_after]:
                    query = Q(start_date__lte=query_date) & (Q(end_date__gt= query_date) | Q(end_date=""))
                    #get_date_data_for_query(key_dates,events,query,query_date,aggregators,available_keys)
                    get_date_data_for_query(query,query_date)

    today = date.today()
    if today not in key_dates.keys():
        query = Q(end_date="")
        #get_date_data_for_query(key_dates,events,query,today,aggregators,available_keys)
        get_date_data_for_query(query,today)
        
    return JsonResponse({'data':key_dates})    

def parties_and_parl(request):
    return render(request,"parlhand/topics/parties_and_parl.html",{})

def topics(request):
    return render(request,"parlhand/topics/topics.html",{})

def longest_serving(request):
    parliamentarians = models.Person.objects.all() #.order_by('service__start_date','-service__end_date')
    out = [] #(days,person)
    for p in parliamentarians:
        days = p.length_of_service
        out.append((days,p))
    out.sort(key=lambda x:x[0])
    return render(request,"parlhand/topics/longest_serving.html",
        {
            "longest":out[-25:][::-1],
            "shortest":out[:25]
        })
        
def all_parliamentarians(request):
    parliamentarians = models.Person.objects.all()

    return render(request,"parlhand/tables/all_past.html",{"parliamentarians":parliamentarians})

def ministerialposition(request,mid):
    ministerialposition = get_object_or_404(models.MinisterialPosition, id=mid)
    return render(request,"parlhand/stuff/ministerialposition.html",{"ministerialposition":ministerialposition})

def ministry(request,mid):
    ministry = get_object_or_404(models.Ministry, number=mid)
    
    ministries = ministry.ministerialappointment_set.order_by("person__surname","type","start_date","end_date").all()
    concurrent_ministry_data = {}
    for m in ministries:
        start = str(m.start_date)
        end = str(m.end_date)
        key = (m.person,str(m.type),start,end)
        mins = concurrent_ministry_data.get(key,'') + ", " + m.position.name
        concurrent_ministry_data[key] = mins


    context = {
        "ministry": ministry,
        "cabinet": ministry.ministerialappointment_set.filter(type=models.MinisterialAppointment.TYPES.Cabinet).count(),
        "inner": ministry.ministerialappointment_set.filter(type=models.MinisterialAppointment.TYPES.Inner).count(),
        "outer": ministry.ministerialappointment_set.filter(type=models.MinisterialAppointment.TYPES.Outer).count(),
        "parlsec": ministry.ministerialappointment_set.filter(type=models.MinisterialAppointment.TYPES.ParlSec).count(),
        "prime_minister": ministry.ministerialappointment_set.get(position__name="Prime Minister").person,
        "concurrent_ministry_data":concurrent_ministry_data
        }
    return render(request,"parlhand/stuff/ministry.html",context)

def electorate(request,eid):
    electorate = get_object_or_404(models.Electorate, id=eid)

    return render(request,"parlhand/stuff/electorate.html",{"electorate":electorate})

def custom_table(request):
    return interrogation_room(request,template='parlhand/tables/custom.html')


from haystack.generic_views import SearchView
from parlhand.forms.search import SpellingSearchQuerySet, SpellingSearchForm

class ParliamentSearchView(SearchView):
    form_class = SpellingSearchForm
    queryset = SpellingSearchQuerySet()
